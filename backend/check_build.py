#!/usr/bin/env python3
import sys
import subprocess
import importlib.util
import os

def check_virtual_env():
    print("=" * 60)
    print("Проверка виртуального окружения...")
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.environ.get('VIRTUAL_ENV') is not None
    )
    
    if in_venv:
        venv_path = os.environ.get('VIRTUAL_ENV', sys.prefix)
        print(f"✅ Работает в виртуальном окружении: {venv_path}")
        return True
    else:
        print("⚠️  ВНИМАНИЕ: Не обнаружено виртуальное окружение!")
        print("   Рекомендуется использовать: source venv/bin/activate")
        print("   Продолжаем проверку...")
        return False

def check_python_version():
    print("=" * 60)
    print("Проверка версии Python...")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Требуется Python 3.10+")
        return False
    print("✅ Версия Python подходит")
    return True

def check_imports():
    print("\n" + "=" * 60)
    print("Проверка импортов...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'sklearn',
        'langchain',
        'langchain_openai',
        'langchain_community',
        'chromadb',
        'openai',
        'pydantic',
    ]
    
    failed = []
    for module in required_modules:
        try:
            if module == 'sklearn':
                importlib.import_module('sklearn')
            else:
                importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Не установлены модули: {', '.join(failed)}")
        return False
    print("\n✅ Все модули установлены")
    return True

def check_project_imports():
    print("\n" + "=" * 60)
    print("Проверка импортов проекта...")
    
    try:
        from config.config import settings
        print("✅ config.config")
        
        from routers import analytics, predict, ask, upload, chat
        print("✅ routers")
        
        from services.data_service import get_data_service
        print("✅ services.data_service")
        
        from services.prediction_service import get_prediction_service
        print("✅ services.prediction_service")
        
        from rag.rag_chain import get_rag_chain
        print("✅ rag.rag_chain")
        
        from rag.vectorstore import get_vectorstore_manager
        print("✅ rag.vectorstore")
        
        print("\n✅ Все импорты проекта работают")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка импорта проекта: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_config():
    print("\n" + "=" * 60)
    print("Проверка конфигурации...")
    
    try:
        from config.config import settings
        
        if not settings.API_KEY:
            print("⚠️  API_KEY не установлен (может быть в .env)")
        else:
            print("✅ API_KEY установлен")
        
        if not settings.DATA_FILE:
            print("⚠️  DATA_FILE не установлен")
        else:
            import os
            if os.path.exists(settings.DATA_FILE):
                print(f"✅ DATA_FILE найден: {settings.DATA_FILE}")
            else:
                print(f"⚠️  DATA_FILE не найден: {settings.DATA_FILE}")
        
        print(f"✅ LLM_MODEL: {settings.LLM_MODEL}")
        print(f"✅ API_BASE_URL: {settings.API_BASE_URL}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def check_data_service():
    print("\n" + "=" * 60)
    print("Проверка data_service...")
    
    try:
        from services.data_service import get_data_service
        data_service = get_data_service()
        
        if data_service.df is None:
            print("❌ DataFrame не загружен")
            return False
        
        print(f"✅ Загружено строк: {len(data_service.df)}")
        print(f"✅ Колонки: {list(data_service.df.columns)[:5]}...")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка data_service: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_fastapi_app():
    print("\n" + "=" * 60)
    print("Проверка FastAPI приложения...")
    
    try:
        from main import app
        
        routes = [route.path for route in app.routes]
        print(f"✅ Приложение создано")
        print(f"✅ Зарегистрировано маршрутов: {len(routes)}")
        print(f"   Примеры: {', '.join(routes[:5])}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("ПРОВЕРКА БИЛДА БЭКЕНДА")
    print("=" * 60)
    
    checks = [
        ("Виртуальное окружение", check_virtual_env),
        ("Версия Python", check_python_version),
        ("Импорты зависимостей", check_imports),
        ("Импорты проекта", check_project_imports),
        ("Конфигурация", check_config),
        ("Data Service", check_data_service),
        ("FastAPI приложение", check_fastapi_app),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Критическая ошибка в {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("ИТОГИ ПРОВЕРКИ")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✅ Все проверки пройдены! Бэкенд готов к запуску.")
        print("\nДля запуска используйте:")
        print("  python run.py")
        print("или")
        print("  uvicorn main:app --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ Некоторые проверки не пройдены. Исправьте ошибки перед деплоем.")
        sys.exit(1)

if __name__ == "__main__":
    main()

