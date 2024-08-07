# logic.py

import json
import uuid
import asyncio
import random
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from PySide6.QtGui import QColor, QPainter
from PySide6.QtCharts import QChart, QLineSeries, QValueAxis, QChartView
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtCore import QThreadPool, QRunnable, Slot
from scpi_client import SCPIClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi

class InfluxWriteWorker(QRunnable):
    def __init__(self, write_api, bucket, points):
        super().__init__()
        self.write_api = write_api
        self.bucket = bucket
        self.points = points

    @Slot()
    def run(self):
        try:
            self.write_api.write(bucket=self.bucket, record=self.points)
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
            print(f"Error details: {type(e).__name__}")
            print(f"Points causing error: {self.points[:5]}")  # 打印前5个点的信息，以便调试

class Logic:
    def __init__(self, ui):
        self.ui = ui
        self.selected_devices = set()
        self.selected_channels = set()
        self.is_running = False
        self.is_paused = False
        self.device_buttons = {}
        self.channel_buttons = {}
        self.setup_button_mappings()
        self.status_messages = []  # 用于存储状态消息
        self.total_measurements = 0
        self.current_measurement = 0
        self.channel_status = {}  # 用于存储每个通道的状态
        self.channel_data = {}  # 用于存储每个通道的数据

        self.full_scale = 5.0  # 满量程为5V
        self.threshold = 3.0  # 阈值为3V

        # Load configuration
        with open('config.json', 'r') as config_file:
            self.config = json.load(config_file)

        # 初始化 InfluxDB 客户端
        self.init_influxdb()

        self.query_api = self.influx_client.query_api()

        # 初始化线程池
        self.threadpool = QThreadPool()

        # Initialize SCPI client
        scpi_config = self.config['scpi_server']
        self.scpi_client = SCPIClient(scpi_config['host'], scpi_config['port'])

        # Initialize measurement variables
        self.current_device = None
        self.current_channel = None
        self.measurement_results = []

        # Setup timer for measurements
        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.perform_measurement)

        # 设置图表
        self.setup_chart()

    def setup(self):
        self.setup_color_matrix()

    def init_influxdb(self):
        influx_config = self.config['influxdb']
        self.influx_client = InfluxDBClient(
            url=influx_config['url'],
            token=influx_config['token'],
            org=influx_config['org']
        )
        self.write_api = self.influx_client.write_api(write_options=ASYNCHRONOUS)
        self.bucket = influx_config['bucket']

    def write_to_influxdb(self, device, channel, voltage_data, status):
        try:
            measurement_id = str(uuid.uuid4())  # 生成唯一的序列ID
            points = []
            base_time = datetime.utcnow()

            for i, voltage in enumerate(voltage_data):
                point = (
                    Point("voltage_measurement")
                    .tag("device", str(device))
                    .tag("channel", str(channel))
                    .tag("measurement_id", measurement_id)
                    .field("voltage", int(voltage))  # Ensure we're writing integers
                    .time(base_time + timedelta(microseconds=i * 1000))
                )
                points.append(point)

            print(
                f"Writing {len(points)} points to InfluxDB for device {device}, channel {channel}, measurement_id {measurement_id}")
            worker = InfluxWriteWorker(self.write_api, self.bucket, points)
            self.threadpool.start(worker)
        except Exception as e:
            print(f"Error in write_to_influxdb: {e}")

    def setup_button_mappings(self):
        # 设置设备按钮 (12台设备)
        for i in range(1, 13):
            button = self.ui.groupBox_2.findChild(QPushButton, f"pushButton_{i}")
            if button:
                self.device_buttons[i] = button

        # 设置通道按钮 (18个通道)
        for i in range(1, 19):
            button = self.ui.groupBox.findChild(QPushButton, f"pushButton_{i}")
            if button:
                self.channel_buttons[i] = button

    def setup_color_matrix(self):
        # 获取表格的尺寸
        table_width = self.ui.colorMatrix.width()
        table_height = self.ui.colorMatrix.height()

        # 计算每个单元格的大小
        cell_width = table_width // 18
        cell_height = table_height // 12

        for row in range(12):
            self.ui.colorMatrix.setRowHeight(row, cell_height)
            for col in range(18):
                self.ui.colorMatrix.setColumnWidth(col, cell_width)
                item = QTableWidgetItem()
                item.setBackground(QColor(row * 20, col * 10, 100))
                self.ui.colorMatrix.setItem(row, col, item)

        # 禁用选择
        self.ui.colorMatrix.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

    def device_button_clicked(self, device_num):
        if device_num in self.device_buttons:
            button = self.device_buttons[device_num]
            if device_num in self.selected_devices:
                self.selected_devices.remove(device_num)
                button.setStyleSheet("")
            else:
                self.selected_devices.add(device_num)
                button.setStyleSheet("background-color: lightblue;")
        else:
            print(f"Device button {device_num} not found")

    def channel_button_clicked(self, channel_num):
        if channel_num in self.channel_buttons:
            button = self.channel_buttons[channel_num]
            if channel_num in self.selected_channels:
                self.selected_channels.remove(channel_num)
                button.setStyleSheet("")
            else:
                self.selected_channels.add(channel_num)
                button.setStyleSheet("background-color: lightblue;")
        else:
            print(f"Channel button {channel_num} not found")

    def device_all_clicked(self):
        all_devices = set(range(1, 13))  # 12台设备
        if self.selected_devices == all_devices:
            self.selected_devices.clear()
        else:
            self.selected_devices = all_devices
        self.update_device_buttons()

    def channel_all_clicked(self):
        all_channels = set(range(1, 19))  # 18个通道
        if self.selected_channels == all_channels:
            self.selected_channels.clear()
        else:
            self.selected_channels = all_channels
        self.update_channel_buttons()

    def update_device_buttons(self):
        for num, button in self.device_buttons.items():
            if num in self.selected_devices:
                button.setStyleSheet("background-color: lightblue;")
            else:
                button.setStyleSheet("")

    def update_channel_buttons(self):
        for num, button in self.channel_buttons.items():
            if num in self.selected_channels:
                button.setStyleSheet("background-color: lightblue;")
            else:
                button.setStyleSheet("")


    def update_status(self, message):
        self.status_messages.append(message)
        # 保持最新的 100 条消息
        self.status_messages = self.status_messages[-100:]
        status_text = "\n".join(self.status_messages)
        self.ui.statusTextEdit.setText(status_text)
        # 滚动到底部
        self.ui.statusTextEdit.verticalScrollBar().setValue(
            self.ui.statusTextEdit.verticalScrollBar().maximum()
        )
        # 同时打印到控制台
        print(message)

    def perform_measurement(self):
        if not self.is_running or self.is_paused:
            return

        result = self.scpi_client.measure(self.current_device, self.current_channel)
        if result:
            voltage_data, status = self.process_measurement(self.current_device, self.current_channel, result)
            self.measurement_results.append(voltage_data)
            status_msg = f"Measured: Device {self.current_device}, Channel {self.current_channel}, Status: {'OK' if status else 'FAIL'}"
            self.update_status(status_msg)

            # 更新进度
            self.current_measurement += 1
            progress = int((self.current_measurement / self.total_measurements) * 100)
            self.ui.progressBar.setValue(progress)
        else:
            status_msg = f"No data received for Device {self.current_device}, Channel {self.current_channel}"
            self.update_status(status_msg)

        # 移动到下一个通道或设备
        self.move_to_next_measurement()

    def move_to_next_measurement(self):
        self.current_channel = self.get_next_channel()
        if self.current_channel is None:
            self.current_device = self.get_next_device()
            if self.current_device is None:
                self.measurement_complete()
            else:
                self.current_channel = min(self.selected_channels)

    def process_measurement(self, device, channel, data):
        # 将数据转换为电压值
        voltage_data = np.array(data) * (self.config['measurement']['full_scale'] / 65535)

        # 判断通道状态
        threshold = self.config['measurement']['threshold']
        ok_points = np.sum(voltage_data > threshold)
        status = bool(ok_points >= (len(voltage_data) * 0.75))  # 转换为 Python 原生布尔类型

        # 更新通道状态
        self.channel_status[(device, channel)] = status

        # 存储通道数据
        self.channel_data[(device, channel)] = voltage_data

        # 更新矩阵显示
        self.update_color_matrix(device, channel, status)

        # 更新图表
        self.update_chart(voltage_data)

        # 异步写入 InfluxDB
        self.write_to_influxdb(device, channel, voltage_data, status)

        return voltage_data, status

    def read_latest_data_from_influxdb(self, device, channel):
        query = f'''
        from(bucket:"{self.bucket}")
        |> range(start: -24h)
        |> filter(fn: (r) => r._measurement == "voltage_measurement")
        |> filter(fn: (r) => r.device == "{device}" and r.channel == "{channel}")
        |> map(fn: (r) => ({{ r with _value: float(v: r._value) }}))
        |> group(columns: ["measurement_id"])
        |> last()
        |> group()
        |> sort(columns: ["_time"])
        '''
        print(f"Executing InfluxDB query: {query}")
        result = self.query_api.query(query=query)

        voltage_data = []
        measurement_id = None
        for table in result:
            for record in table.records:
                voltage = record.get_value()
                if voltage is not None:
                    voltage_data.append(int(float(voltage)))  # Convert to int after ensuring it's a float
                    if measurement_id is None:
                        measurement_id = record.values.get('measurement_id')

        print(f"Query result: Retrieved {len(voltage_data)} data points for measurement_id {measurement_id}")
        if voltage_data:
            print(f"First 5 points: {voltage_data[:5]}...")
            print(f"Last 5 points: {voltage_data[-5:]}...")
        else:
            print("No data retrieved")
        return voltage_data, measurement_id

    def display_channel_data(self, device, channel):
        if not self.is_running:
            try:
                data, measurement_id = self.read_latest_data_from_influxdb(device, channel)
                if data:
                    # 转换为浮点数进行显示
                    full_scale = self.config['measurement']['full_scale']
                    voltage_data = [d * (full_scale / 65535) for d in data]
                    self.update_chart(voltage_data)
                    self.chart.setTitle(f"Device {device}, Channel {channel}, Measurement ID: {measurement_id}")
                    self.update_status(f"Displaying data for Device {device}, Channel {channel}, Measurement ID: {measurement_id}")
                else:
                    print(f"No data retrieved for Device {device}, Channel {channel}")
                    self.update_status(f"No data available in InfluxDB for Device {device}, Channel {channel}")
                    self.clear_chart()
            except Exception as e:
                print(f"Error in display_channel_data: {e}")
                print(f"Error details: {type(e).__name__}, {str(e)}")
                self.update_status(f"Error retrieving data for Device {device}, Channel {channel}")
                self.clear_chart()

    def update_color_matrix(self, device, channel, status):
        item = self.ui.colorMatrix.item(device - 1, channel - 1)
        if item:
            color = QColor(0, 255, 0) if status else QColor(255, 0, 0)
            item.setBackground(color)

    def update_chart(self, voltage_data):
        print(f"Updating chart with {len(voltage_data)} data points")  # 调试信息
        self.series.clear()
        for i, value in enumerate(voltage_data):
            self.series.append(i, value)

        # 更新 Y 轴范围
        min_voltage = min(voltage_data)
        max_voltage = max(voltage_data)
        y_range = max_voltage - min_voltage
        self.axis_y.setRange(max(0, min_voltage - 0.1 * y_range), max_voltage + 0.1 * y_range)
        self.axis_y.setTitleText("Voltage (V)")

        # 更新 X 轴范围
        self.axis_x.setRange(0, len(voltage_data) - 1)
        self.axis_x.setTitleText("Sample")

        # 强制重绘图表
        self.ui.chartView.repaint()

    def clear_chart(self):
        self.series.clear()
        self.chart.setTitle("No Data")
        self.ui.chartView.repaint()

    def setup_chart(self):
        self.chart = QChart()
        self.ui.chartView.setChart(self.chart)
        self.ui.chartView.setRenderHint(QPainter.Antialiasing)

        self.series = QLineSeries()
        self.chart.addSeries(self.series)

        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        # 初始设置，实际范围将在 update_chart 中更新
        self.axis_x.setRange(0, 1000)
        self.axis_y.setRange(0, self.full_scale)

        self.chart.setTitle("Measurement Data")
        self.axis_x.setTitleText("Sample")
        self.axis_y.setTitleText("Voltage (V)")

        # 设置图表主题
        self.chart.setTheme(QChart.ChartThemeBlueCerulean)

        # 禁用图例
        self.chart.legend().hide()

    def get_next_channel(self):
        channels = sorted(self.selected_channels)
        try:
            return channels[channels.index(self.current_channel) + 1]
        except IndexError:
            return None

    def get_next_device(self):
        devices = sorted(self.selected_devices)
        try:
            return devices[devices.index(self.current_device) + 1]
        except IndexError:
            return None

    def start_action(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.ui.progressBar.setValue(0)
            self.measurement_results = []
            self.current_device = min(self.selected_devices) if self.selected_devices else None
            self.current_channel = min(self.selected_channels) if self.selected_channels else None
            if self.current_device and self.current_channel:
                self.total_measurements = len(self.selected_devices) * len(self.selected_channels)
                self.current_measurement = 0
                self.measurement_timer.start(100)  # 每100毫秒执行一次测量
                self.update_status("Measurement started")
            else:
                self.update_status("No devices or channels selected")
                self.is_running = False

    def pause_resume_action(self):
        if self.is_running:
            if self.is_paused:
                # 恢复测量
                self.is_paused = False
                self.measurement_timer.start(100)
                self.update_status("Measurement resumed")
                self.ui.pushButton_34.setText("PAUSE")
            else:
                # 暂停测量
                self.is_paused = True
                self.measurement_timer.stop()
                self.update_status("Measurement paused")
                self.ui.pushButton_34.setText("RESUME")
        else:
            self.update_status("No measurement in progress")

    def stop_action(self):
        if self.is_running:
            self.is_running = False
            self.measurement_timer.stop()
            self.update_status("Measurement stopped")

    def reset_action(self):
        self.is_running = False
        self.is_paused = False
        self.measurement_timer.stop()
        self.ui.progressBar.setValue(0)
        self.selected_devices.clear()
        self.selected_channels.clear()
        self.update_device_buttons()
        self.update_channel_buttons()
        self.series.clear()
        self.chart.setTitle("Measurement Data")
        self.ui.chartView.repaint()
        self.channel_status.clear()
        self.reset_color_matrix()
        self.total_measurements = 0
        self.current_measurement = 0
        self.update_status("Reset completed")
        self.ui.pushButton_34.setText("PAUSE")
        self.channel_data.clear()

        # 等待所有异步写入任务完成
        self.threadpool.waitForDone()

        # 关闭 InfluxDB 客户端连接
        self.influx_client.close()

        # 重新初始化 InfluxDB 客户端
        self.init_influxdb()

    def reset_color_matrix(self):
        for row in range(self.ui.colorMatrix.rowCount()):
            for col in range(self.ui.colorMatrix.columnCount()):
                item = self.ui.colorMatrix.item(row, col)
                if item:
                    item.setBackground(QColor(200, 200, 200))  # 设置为灰色

    def measurement_complete(self):
        self.is_running = False
        self.measurement_timer.stop()
        self.ui.progressBar.setValue(100)
        self.update_status(f"Measurement complete. Total measurements: {self.current_measurement}")

    def __del__(self):
        # 确保在对象被销毁时等待所有异步写入任务完成并关闭 InfluxDB 客户端连接
        if hasattr(self, 'threadpool'):
            self.threadpool.waitForDone()
        if hasattr(self, 'influx_client'):
            self.influx_client.close()