""" Модуль окна добавления трансакции пользовательского интерфейса программы"""

from PySide6.QtWidgets import (QMainWindow, QLabel, QComboBox)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, QInputDialog)
from bookkeeper.controller.crud_controller import CrudController
from datetime import datetime
from pony.orm import *
from bookkeeper.models.entities import Category



class AddWindow(QMainWindow):
    """Окно добавления строки расходов"""
    def __init__(self):
        super().__init__()

        self.controller = CrudController()
        self.setWindowTitle("Программа для ведения бюджета")
        self.setFixedSize(500, 500)

        self.layout = QVBoxLayout()

        self.date = QLabel('Дата: ')
        self.amount = QLabel('Сумма: ')
        self.comment = QLabel('Комментарий: ')
        self.layout.addWidget(self.date)
        self.edit_date = QLineEdit()
        self.layout.addWidget(self.edit_date)
        self.layout.addWidget(self.amount)
        self.edit_amount = QLineEdit()
        self.layout.addWidget(self.edit_amount)
        self.layout.addWidget(self.comment)
        self.edit_comment = QLineEdit()
        self.layout.addWidget(self.edit_comment)

        """Выпадающий список выбора категории расходов"""
        self.category = QComboBox(self)
        self.layout.addWidget(QLabel('Выберите категорию расхода:'))
        self.layout.addWidget(self.category)
        with db_session:
            categories = Category.select()
            for category in categories:
                self.category.addItem(category.name)

        self.budget_button = QPushButton('Записать расходы')
        self.layout.addWidget(self.budget_button)
        self.budget_button.clicked.connect(self.on_expense_button_click)



        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    def set_controller(self, controller):
        self.controller = controller

    def create_expense(self):
        params = {
            'amount': float(self.edit_amount.text()),
            'expense_date': datetime.strptime(self.edit_date.text(), '%d.%m.%y'),
            'comment': str(self.edit_comment.text()),
            'category_id': self.category.currentIndex()  # значения идентификатора категории
        }

    def on_expense_button_click(self):
        expense_date = datetime.strptime(self.edit_date.text(), '%d.%m.%y')
        self.controller.create('Expense', {
            'amount': float(self.edit_amount.text()),
            'expense_date': expense_date,
            'comment': str(self.edit_comment.text()),
            'category_id': self.category.currentIndex() + 1  # 'category' должен быть выбран из QComboBox
        })  # категории записывались в базу с понижением по id на 1. Сработала такая заглушка "+1".
        # Найти причину
        self.create_expense()

    def refresh_categories(self):
        cats = self.controller.read('Category')
        self.category.addItems(cats)


    @db_session
    def on_create_category_button_click(self):
        """ Декоратор для обертывания создания новой категории в транзакцию """
        new_category_name, ok_pressed = QInputDialog.getText(self, "Введите название категории", "Название категории:")

        if ok_pressed:
            new_category = Category(name=new_category_name)

    def load_data_from_db(self):
        """ Функция для отображения данных о расходах в главном окне пользовательского интерфейса"""
        db_connection = sqlite3.connect('db')
        cursor = db_connection.cursor()
        cursor.execute("SELECT amount, expense_date, category, comment FROM expenses")

        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.table.setItem(i, j, item)

        db_connection.close()
