""" Модуль окна добавления трансакции пользовательского интерфейса программы"""
from PySide6.QtWidgets import (QMainWindow, QLabel, QComboBox, QTableWidget, QAbstractItemView)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, QInputDialog, QMessageBox)
from bookkeeper.controller.crud_controller import CrudController
from datetime import datetime
from bookkeeper.models.entities import *

from bookkeeper.models.entities import *



from PySide6.QtWidgets import QHeaderView



from pony.orm import *
# Подключение к существующей базе данных

from bookkeeper.models.entities import Category
from bookkeeper.models.entities import Budget
from bookkeeper.models.entities import db

def select_categories_from_db():
    categories = [category.name for category in select(c for c in Category)]
    return categories

def delete_category_from_db(category_name):
    category = select(c for c in Category if c.name == category_name)[:]
    if category:
        delete(c for c in Category if c.name == category_name)



class AddWindow(QMainWindow):
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




        # Определение обработчика события

        self.create_category_button = QPushButton('Создать категорию')
        self.layout.addWidget(self.create_category_button)
        self.create_category_button.clicked.connect(self.on_create_category_button_click)


        self.delete_category_button = QPushButton('Удалить категорию')
        self.layout.addWidget(self.delete_category_button)
        self.delete_category_button.clicked.connect(self.on_delete_category_button_click)


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
            'category_id': self.category.currentIndex()  # Пример значения идентификатора категории
        }




    def on_expense_button_click(self):
        expense_date = datetime.strptime(self.edit_date.text(), '%d.%m.%y')
        self.controller.create('Expense', {
            'amount': float(self.edit_amount.text()),
            'expense_date': expense_date,
            'comment': str(self.edit_comment.text()),
            'category_id': self.category.currentIndex()  # Предполагая, что 'category' должен быть выбран из QComboBox
        })
        self.create_expense()







    def refresh_categories(self):
        cats = self.controller.read('Category')
        self.category.addItems(cats)

    def on_create_category_button_click(self):
        # Обработка нажатия на кнопку "Создать категорию"
        pass

    def on_delete_category_button_click(self):
        # Обработка нажатия на кнопку "Удалить категорию"
        pass






    # Декоратор для обертывания создания новой категории в транзакцию
    @db_session
    def on_create_category_button_click(self):
        new_category_name, ok_pressed = QInputDialog.getText(self, "Введите название категории", "Название категории:")

        if ok_pressed:
            new_category = Category(name=new_category_name)




    @db_session
    def on_delete_category_button_click(self):
        categories = select_categories_from_db()
        category, ok = QInputDialog.getItem(self, "Выберите категорию", "Категория:", categories, 0, False)

        if ok:
            reply = QMessageBox.question(self, 'Подтверждение удаления',
                                         f"Вы уверены, что хотите удалить категорию {category}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                delete_category_from_db(category)  # Замените на свой метод удаления категории из базы данных


    def load_data_from_db(self):
        db_connection = sqlite3.connect('db')  # Подставьте имя вашей базы данных
        cursor = db_connection.cursor()
        cursor.execute("SELECT amount, expense_date, category, comment FROM expenses")

        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.table.setItem(i, j, item)

        db_connection.close()


