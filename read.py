import sys
import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')  # 确保使用Qt5后端
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QFileDialog, QLabel, QSpinBox,
                             QLineEdit, QFormLayout, QSizePolicy, QMessageBox,
                             QGroupBox, QFrame, QSplitter, QTabWidget, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


# 全局变量，用于决定是否使用英文标签  
USE_ENGLISH_LABELS = True  # 强制使用英文标签

def configure_matplotlib_fonts():
    # 全部指定 SimHei（黑体），确保中文正常显示
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False   # 负号正常显示
    print("Matplotlib 字体已全部设置为 SimHei")


class DataVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('多分量数据可视化工具')
        self.setGeometry(100, 100, 1400, 900)
        
        # 应用样式表
        self.apply_stylesheet()

        # 创建主部件和布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建顶部标题
        title_label = QLabel('多分量信号数据可视化分析平台')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('''
            font-size: 24px;
            color: #2c3e50;
            margin: 10px;
            font-weight: bold;
        ''')
        main_layout.addWidget(title_label)
        
        # 创建分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #bdc3c7; margin: 5px 0px;")
        main_layout.addWidget(separator)

        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧控制面板
        control_panel = QGroupBox("控制面板")
        control_panel.setStyleSheet('''
            QGroupBox {
                background-color: #f5f5f5;
                border-radius: 10px;
                border: 1px solid #dcdcdc;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        ''')
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 20, 15, 15)
        control_layout.setSpacing(15)

        # 文件选择组
        file_group = QGroupBox("数据文件")
        file_group.setStyleSheet('''
            QGroupBox {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
            }
        ''')
        file_layout = QVBoxLayout(file_group)
        
        self.file_path_label = QLabel('未选择文件')
        self.file_path_label.setStyleSheet('''
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            color: #555;
        ''')
        self.file_path_label.setWordWrap(True)
        
        select_file_btn = QPushButton('选择数据文件')
        select_file_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
        ''')
        select_file_btn.setMinimumHeight(35)
        select_file_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(select_file_btn)
        
        # 参数设置组
        params_group = QGroupBox("参数设置")
        params_group.setStyleSheet('''
            QGroupBox {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
            }
        ''')
        params_layout = QFormLayout(params_group)
        params_layout.setVerticalSpacing(10)
        params_layout.setContentsMargins(15, 15, 15, 15)
        
        # 分量数选择
        self.component_spinbox = QSpinBox()
        self.component_spinbox.setRange(1, 4)
        self.component_spinbox.setValue(3)
        self.component_spinbox.setStyleSheet('''
            QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #f0f0f0;
                border-radius: 2px;
            }
        ''')
        self.component_spinbox.setMinimumHeight(30)
        
        # 采样率输入
        self.sampling_rate_input = QLineEdit('1000')
        self.sampling_rate_input.setStyleSheet('''
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background: white;
            }
        ''')
        self.sampling_rate_input.setMinimumHeight(30)
        
        # 绘图颜色选择
        self.color_theme = QComboBox()
        self.color_theme.addItems(["默认", "暖色调", "冷色调", "灰度", "彩虹色"])
        self.color_theme.setStyleSheet('''
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background: white;
            }
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #bdc3c7;
                background: #f0f0f0;
            }
        ''')
        self.color_theme.setMinimumHeight(30)
        
        # 添加到参数布局
        components_label = QLabel("分量数:")
        sampling_label = QLabel("采样率(Hz):")
        color_label = QLabel("颜色主题:")
        
        label_style = '''
            font-weight: normal;
            color: #444;
        '''
        components_label.setStyleSheet(label_style)
        sampling_label.setStyleSheet(label_style)
        color_label.setStyleSheet(label_style)
        
        params_layout.addRow(components_label, self.component_spinbox)
        params_layout.addRow(sampling_label, self.sampling_rate_input)
        params_layout.addRow(color_label, self.color_theme)
        
        # 操作按钮组
        actions_group = QGroupBox("操作")
        actions_group.setStyleSheet('''
            QGroupBox {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
            }
        ''')
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)
        
        # 可视化按钮
        visualize_btn = QPushButton('数据可视化')
        visualize_btn.setStyleSheet('''
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        ''')
        visualize_btn.setMinimumHeight(40)
        visualize_btn.clicked.connect(self.visualize_data)
        
        # 保存图像按钮
        save_btn = QPushButton('保存图像')
        save_btn.setStyleSheet('''
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        ''')
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_figure)
        
        actions_layout.addWidget(visualize_btn)
        actions_layout.addWidget(save_btn)
        
        # 添加所有组到控制面板
        control_layout.addWidget(file_group)
        control_layout.addWidget(params_group)
        control_layout.addWidget(actions_group)
        control_layout.addStretch(1)
        
        # 右侧图形显示区域
        display_panel = QWidget()
        display_layout = QVBoxLayout(display_panel)
        display_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标签指示图表区域
        chart_label = QLabel("数据可视化区域")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet('''
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 10px;
        ''')
        display_layout.addWidget(chart_label)
        
        # 创建 Figure
        self.figure = plt.Figure(figsize=(24, 8), dpi=100)
        self.figure.patch.set_facecolor('#f8f9fa')
        
        # 创建 FigureCanvas
        self.canvas = FigureCanvas(self.figure)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(size_policy)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid #e0e0e0; border-radius: 5px;")
        
        # 初始化时显示欢迎信息
        welcome_ax = self.figure.add_subplot(111)
        # 设置网格背景
        welcome_ax.grid(False)
        welcome_ax.set_facecolor('#f8f9fa')
        welcome_ax.spines['top'].set_visible(False)
        welcome_ax.spines['right'].set_visible(False)
        welcome_ax.spines['bottom'].set_visible(False)
        welcome_ax.spines['left'].set_visible(False)
        
        # 在欢迎界面绘制示例波形
        x = np.linspace(0, 10, 100)
        welcome_ax.plot(x, np.sin(x), color='#3498db', alpha=0.6, linewidth=2)
        welcome_ax.plot(x, 0.5*np.sin(2*x), color='#2ecc71', alpha=0.6, linewidth=2)
        welcome_ax.plot(x, 0.3*np.sin(3*x), color='#e74c3c', alpha=0.6, linewidth=2)
        
        # 欢迎文本使用中文，但为了避免字体问题，简化文本内容
        welcome_text = "数据可视化工具\n请选择数据文件"
            
        welcome_ax.text(5, 0, welcome_text, 
                    ha='center', va='center', fontsize=18, color='#2c3e50',
                    bbox=dict(boxstyle="round,pad=0.5", fc='white', ec='#bdc3c7', alpha=0.9))
        welcome_ax.axis('off')
        self.canvas.draw()
        
        # 添加到显示布局
        display_layout.addWidget(self.canvas)
        
        # 将面板添加到分割器
        splitter.addWidget(control_panel)
        splitter.addWidget(display_panel)
        
        # 设置分割比例 (1:3)
        splitter.setSizes([300, 900])
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
        
        # 添加状态栏信息
        status_bar = QLabel("准备就绪 | 支持.dat和.txt格式文件 | 最多支持4个分量")
        status_bar.setStyleSheet('''
            background-color: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            padding: 5px;
            color: #7f8c8d;
            font-size: 12px;
        ''')
        main_layout.addWidget(status_bar)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 存储文件路径
        self.file_path = None
        
    def apply_stylesheet(self):
        """应用全局样式表"""
        self.setStyleSheet('''
            QMainWindow {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
            }
            QToolTip {
                background-color: #2c3e50;
                color: white;
                border: none;
                opacity: 200;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        ''')

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择数据文件',
            '',
            '数据文件 (*.dat *.txt)'
        )

        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(file_path)

    def visualize_data(self):
        if not self.file_path:
            QMessageBox.warning(self, '警告', '请先选择文件')
            return

        try:
            # 读取数据
            if self.file_path.endswith('.dat'):
                with open(self.file_path, 'rb') as f:
                    data = np.fromfile(f, dtype=np.int32)
            else:
                data = np.loadtxt(self.file_path)
                data = data.astype(np.int32)

            # 检查数据是否为空
            if len(data) == 0:
                QMessageBox.warning(self, '警告', '文件内容为空')
                return

            # 获取用户配置
            components = self.component_spinbox.value()
            f_s = float(self.sampling_rate_input.text())
            color_theme = self.color_theme.currentText()

            # 清空 figure
            self.figure.clf()

            # 设置图表样式
            self.figure.patch.set_facecolor('#f8f9fa')
            
            # 设置绘图风格
            plt.style.use('seaborn-v0_8-whitegrid')
            
            # 根据主题选择颜色
            if color_theme == "默认":
                colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
            elif color_theme == "暖色调":
                colors = ['#e74c3c', '#f39c12', '#f1c40f', '#d35400']
            elif color_theme == "冷色调":
                colors = ['#3498db', '#2980b9', '#1abc9c', '#3498db']
            elif color_theme == "灰度":
                colors = ['#2c3e50', '#7f8c8d', '#bdc3c7', '#34495e']
            elif color_theme == "彩虹色":
                colors = ['#e74c3c', '#f1c40f', '#2ecc71', '#3498db']

            # 动态创建子图
            self.axes = self.figure.subplots(2, components)

            if components == 1:
                self.axes = self.axes.reshape(2, 1)

            # 分割数据
            length = len(data) // components
            component_data = [data[i::components] for i in range(components)]

            # 频率轴
            freq = np.linspace(0, f_s/2, length//2)  # 只显示到一半频率 (奈奎斯特频率)

            # 根据是否能显示中文设置标签
            if USE_ENGLISH_LABELS:
                time_titles = [f'Component {i+1} Time Domain' for i in range(components)]
                freq_titles = [f'Component {i+1} Frequency Domain' for i in range(components)]
                x_label_time = 'Sample Points'
                y_label_time = 'Amplitude'
                x_label_freq = 'Frequency (Hz)'
                y_label_freq = 'Amplitude'
            else:
                time_titles = [f'分量 {i+1} 时域信号' for i in range(components)]
                freq_titles = [f'分量 {i+1} 频域信号' for i in range(components)]
                x_label_time = '采样点'
                y_label_time = '幅值'
                x_label_freq = '频率 (Hz)'
                y_label_freq = '幅值'
            
            # 绘制时域和频域信号
            for i in range(components):
                # 时域
                self.axes[0, i].plot(component_data[i], color=colors[i], linewidth=1.5)
                self.axes[0, i].set_title(time_titles[i], fontsize=12, pad=10)
                self.axes[0, i].set_xlabel(x_label_time, fontsize=10)
                self.axes[0, i].set_ylabel(y_label_time, fontsize=10)
                self.axes[0, i].grid(True, linestyle='--', alpha=0.7)
                self.axes[0, i].spines['top'].set_visible(False)
                self.axes[0, i].spines['right'].set_visible(False)
                
                # 为奇数个分量时添加边框
                if components % 2 == 1 and i == components - 1:
                    self.axes[0, i].spines['top'].set_visible(False)
                    self.axes[0, i].spines['right'].set_visible(False)

                # 频域 - 使用更现代的显示方式
                fft_data = np.abs(np.fft.fft(component_data[i])[:length//2])  # 只取一半
                self.axes[1, i].plot(freq, fft_data, color=colors[i], linewidth=1.5)
                self.axes[1, i].set_title(freq_titles[i], fontsize=12, pad=10)
                self.axes[1, i].set_xlabel(x_label_freq, fontsize=10)
                self.axes[1, i].set_ylabel(y_label_freq, fontsize=10)
                self.axes[1, i].grid(True, linestyle='--', alpha=0.7)
                self.axes[1, i].spines['top'].set_visible(False)
                self.axes[1, i].spines['right'].set_visible(False)
                
                # 对频域图进行美化处理
                if np.max(fft_data) > 0:
                    self.axes[1, i].set_ylim(0, np.max(fft_data) * 1.1)

            # 调整布局并刷新画布
            self.figure.tight_layout()
            self.canvas.draw()

            # 显示画布
            self.canvas.show()

        except Exception as e:
            QMessageBox.critical(self, '错误', f'数据处理失败: {str(e)}')

    def save_figure(self):
        # 检查是否已经绘图
        if not hasattr(self, 'axes'):
            QMessageBox.warning(self, '提示', '请先可视化数据后再保存图像')
            return

        # 弹出保存文件对话框
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存图像',
            '',
            '图像文件 (*.png *.jpg *.pdf)'
        )

        if save_path:
            try:
                # 保存前优化图像布局
                self.figure.tight_layout(pad=2.0)
                self.figure.savefig(save_path, dpi=300, bbox_inches='tight')
                
                # 显示成功消息
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle('成功')
                msg.setText('图像保存成功')
                msg.setInformativeText(f'图像已保存到: {save_path}')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存图像失败: {str(e)}')


def main():
    app = QApplication(sys.argv)
    # 配置matplotlib中文字体
    configure_matplotlib_fonts()
    main_window = DataVisualizationApp()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()