#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования системы управления документами
"""

from document_workflow import DocumentManager, DocumentStatus


def create_sample_documents():
    """Создание примеров документов для демонстрации"""
    manager = DocumentManager("sample_documents.json")
    
    # Создание примеров документов
    doc1 = manager.add_document(
        "Техническое задание на разработку веб-приложения",
        "Подробное описание требований к новому веб-приложению для управления задачами"
    )
    
    doc2 = manager.add_document(
        "Политика информационной безопасности",
        "Документ, регламентирующий правила работы с конфиденциальной информацией"
    )
    
    doc3 = manager.add_document(
        "Руководство пользователя",
        "Инструкция по использованию системы управления документами"
    )
    
    # Изменение статусов для демонстрации workflow
    manager.change_document_status(doc1.id, DocumentStatus.REVIEW, "Отправлено на рассмотрение команде разработки")
    manager.change_document_status(doc1.id, DocumentStatus.APPROVED, "Одобрено техническим директором")
    
    manager.change_document_status(doc2.id, DocumentStatus.REVIEW, "Передано в юридический отдел")
    manager.change_document_status(doc2.id, DocumentStatus.REJECTED, "Требуются дополнения по разделу 'Обработка персональных данных'")
    
    print("Созданы примеры документов в файле 'sample_documents.json'")
    print("Запустите приложение с этим файлом для просмотра примеров:")
    print("python document_workflow.py")


if __name__ == "__main__":
    create_sample_documents()