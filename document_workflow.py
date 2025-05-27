#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Консольное приложение для управления документами и их согласованием
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class DocumentStatus(Enum):
    """Статусы документов"""
    DRAFT = "Черновик"
    REVIEW = "На рассмотрении"
    APPROVED = "Согласован"
    REJECTED = "Отклонен"
    ARCHIVED = "Архивирован"


class Document:
    """Класс для представления документа"""
    
    def __init__(self, doc_id: int, title: str, description: str = ""):
        self.id = doc_id
        self.title = title
        self.description = description
        self.status = DocumentStatus.DRAFT
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
        self.history = [f"Документ создан ({self.created_at})"]
    
    def change_status(self, new_status: DocumentStatus, comment: str = ""):
        """Изменение статуса документа"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        history_entry = f"Статус изменен с '{old_status.value}' на '{new_status.value}'"
        if comment:
            history_entry += f" ({comment})"
        history_entry += f" - {self.updated_at}"
        
        self.history.append(history_entry)
    
    def to_dict(self) -> dict:
        """Преобразование объекта в словарь для сохранения"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'history': self.history
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Создание объекта из словаря"""
        doc = cls(data['id'], data['title'], data['description'])
        doc.status = DocumentStatus[data['status']]
        doc.created_at = data['created_at']
        doc.updated_at = data['updated_at']
        doc.history = data['history']
        return doc


class DocumentManager:
    """Менеджер для управления документами"""
    
    def __init__(self, data_file: str = "documents.json"):
        self.data_file = data_file
        self.documents: Dict[int, Document] = {}
        self.next_id = 1
        self.load_documents()
    
    def load_documents(self):
        """Загрузка документов из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for doc_data in data.get('documents', []):
                        doc = Document.from_dict(doc_data)
                        self.documents[doc.id] = doc
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
    
    def save_documents(self):
        """Сохранение документов в файл"""
        data = {
            'documents': [doc.to_dict() for doc in self.documents.values()],
            'next_id': self.next_id
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_document(self, title: str, description: str = "") -> Document:
        """Добавление нового документа"""
        doc = Document(self.next_id, title, description)
        self.documents[self.next_id] = doc
        self.next_id += 1
        self.save_documents()
        return doc
    
    def get_document(self, doc_id: int) -> Optional[Document]:
        """Получение документа по ID"""
        return self.documents.get(doc_id)
    
    def get_all_documents(self) -> List[Document]:
        """Получение всех документов"""
        return list(self.documents.values())
    
    def change_document_status(self, doc_id: int, new_status: DocumentStatus, comment: str = "") -> bool:
        """Изменение статуса документа"""
        doc = self.get_document(doc_id)
        if doc:
            doc.change_status(new_status, comment)
            self.save_documents()
            return True
        return False


class DocumentWorkflowApp:
    """Главный класс консольного приложения"""
    
    def __init__(self):
        self.manager = DocumentManager()
    
    def display_menu(self):
        """Отображение главного меню"""
        print("\n" + "="*50)
        print("СИСТЕМА УПРАВЛЕНИЯ ДОКУМЕНТАМИ")
        print("="*50)
        print("1. Добавить документ")
        print("2. Показать все документы")
        print("3. Изменить статус документа")
        print("4. Показать историю документа")
        print("5. Поиск документов по статусу")
        print("0. Выход")
        print("-"*50)
    
    def add_document(self):
        """Добавление нового документа"""
        print("\n--- ДОБАВЛЕНИЕ ДОКУМЕНТА ---")
        title = input("Введите название документа: ").strip()
        if not title:
            print("Ошибка: Название документа не может быть пустым!")
            return
        
        description = input("Введите описание документа (необязательно): ").strip()
        
        doc = self.manager.add_document(title, description)
        print(f"✓ Документ #{doc.id} '{doc.title}' успешно создан!")
    
    def show_all_documents(self):
        """Отображение всех документов"""
        documents = self.manager.get_all_documents()
        
        if not documents:
            print("\nДокументы не найдены.")
            return
        
        print(f"\n--- СПИСОК ДОКУМЕНТОВ ({len(documents)} шт.) ---")
        print(f"{'ID':<4} {'Название':<30} {'Статус':<15} {'Обновлен':<20}")
        print("-" * 75)
        
        for doc in sorted(documents, key=lambda x: x.id):
            print(f"{doc.id:<4} {doc.title[:28]:<30} {doc.status.value:<15} {doc.updated_at:<20}")
    
    def change_document_status(self):
        """Изменение статуса документа"""
        self.show_all_documents()
        
        if not self.manager.get_all_documents():
            return
        
        print("\n--- ИЗМЕНЕНИЕ СТАТУСА ---")
        try:
            doc_id = int(input("Введите ID документа: "))
        except ValueError:
            print("Ошибка: Некорректный ID документа!")
            return
        
        doc = self.manager.get_document(doc_id)
        if not doc:
            print(f"Ошибка: Документ с ID {doc_id} не найден!")
            return
        
        print(f"\nТекущий документ: '{doc.title}'")
        print(f"Текущий статус: {doc.status.value}")
        
        # Показ доступных статусов
        print("\nДоступные статусы:")
        statuses = list(DocumentStatus)
        for i, status in enumerate(statuses, 1):
            print(f"{i}. {status.value}")
        
        try:
            choice = int(input("\nВыберите новый статус (номер): "))
            if 1 <= choice <= len(statuses):
                new_status = statuses[choice - 1]
                comment = input("Добавить комментарий (необязательно): ").strip()
                
                self.manager.change_document_status(doc_id, new_status, comment)
                print(f"✓ Статус документа изменен на '{new_status.value}'")
            else:
                print("Ошибка: Некорректный выбор!")
        except ValueError:
            print("Ошибка: Введите число!")
    
    def show_document_history(self):
        """Отображение истории документа"""
        self.show_all_documents()
        
        if not self.manager.get_all_documents():
            return
        
        print("\n--- ИСТОРИЯ ДОКУМЕНТА ---")
        try:
            doc_id = int(input("Введите ID документа: "))
        except ValueError:
            print("Ошибка: Некорректный ID документа!")
            return
        
        doc = self.manager.get_document(doc_id)
        if not doc:
            print(f"Ошибка: Документ с ID {doc_id} не найден!")
            return
        
        print(f"\nИстория документа '{doc.title}' (ID: {doc.id})")
        print("Описание:", doc.description or "Отсутствует")
        print("Текущий статус:", doc.status.value)
        print("\nИстория изменений:")
        print("-" * 60)
        
        for i, entry in enumerate(doc.history, 1):
            print(f"{i}. {entry}")
    
    def search_documents_by_status(self):
        """Поиск документов по статусу"""
        print("\n--- ПОИСК ПО СТАТУСУ ---")
        print("Доступные статусы:")
        statuses = list(DocumentStatus)
        for i, status in enumerate(statuses, 1):
            print(f"{i}. {status.value}")
        
        try:
            choice = int(input("\nВыберите статус (номер): "))
            if 1 <= choice <= len(statuses):
                selected_status = statuses[choice - 1]
                
                filtered_docs = [doc for doc in self.manager.get_all_documents() 
                               if doc.status == selected_status]
                
                if not filtered_docs:
                    print(f"\nДокументы со статусом '{selected_status.value}' не найдены.")
                    return
                
                print(f"\n--- ДОКУМЕНТЫ СО СТАТУСОМ '{selected_status.value}' ({len(filtered_docs)} шт.) ---")
                print(f"{'ID':<4} {'Название':<30} {'Обновлен':<20}")
                print("-" * 60)
                
                for doc in sorted(filtered_docs, key=lambda x: x.id):
                    print(f"{doc.id:<4} {doc.title[:28]:<30} {doc.updated_at:<20}")
            else:
                print("Ошибка: Некорректный выбор!")
        except ValueError:
            print("Ошибка: Введите число!")
    
    def run(self):
        """Запуск приложения"""
        print("Добро пожаловать в систему управления документами!")
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Выберите действие: ").strip()
                
                if choice == '1':
                    self.add_document()
                elif choice == '2':
                    self.show_all_documents()
                elif choice == '3':
                    self.change_document_status()
                elif choice == '4':
                    self.show_document_history()
                elif choice == '5':
                    self.search_documents_by_status()
                elif choice == '0':
                    print("\nДо свидания!")
                    break
                else:
                    print("Ошибка: Некорректный выбор! Введите число от 0 до 5.")
                
                input("\nНажмите Enter для продолжения...")
                
            except KeyboardInterrupt:
                print("\n\nПрограмма завершена пользователем.")
                break
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                input("Нажмите Enter для продолжения...")


def main():
    """Точка входа в программу"""
    app = DocumentWorkflowApp()
    app.run()


if __name__ == "__main__":
    main()