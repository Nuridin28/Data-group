# Hugging Face EmbeddingGemma Integration

## Изменения

Проект теперь использует **Hugging Face EmbeddingGemma** вместо OpenAI embeddings.

### Модель
- **Модель**: `google/embeddinggemma-300m`
- **Размерность**: 768 (можно урезать до 512, 256, 128)
- **Источник**: [Hugging Face](https://huggingface.co/google/embeddinggemma-300m)

### Конфигурация в `.env`

```env
# Hugging Face Configuration for Embeddings
HUGGINGFACE_API_TOKEN=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
EMBEDDING_MODEL=google/embeddinggemma-300m
EMBEDDING_DEVICE=cpu
```

### Преимущества

1. **Локальные embeddings** - не требует API вызовов для embeddings
2. **Бесплатно** - нет платы за использование
3. **Быстро** - после первой загрузки работает локально
4. **Мультиязычность** - обучена на 100+ языках
5. **Оптимизирована для поиска** - специально для retrieval задач

### Как это работает

1. **Первая загрузка**: Модель скачивается с Hugging Face (требуется токен)
2. **Создание embeddings**: Каждая строка CSV конвертируется в вектор 768 размерности
3. **Хранение**: Embeddings сохраняются в ChromaDB в `./vectorstore`
4. **Поиск**: При запросах используются локальные embeddings для поиска релевантных данных

### Архитектура

```
CSV Data → Text Chunks → EmbeddingGemma → Vectors (768d) → ChromaDB
                                                                    ↓
Query → EmbeddingGemma → Query Vector → Similarity Search → Relevant Chunks → LLM
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

Новые зависимости:
- `sentence-transformers>=2.2.0`
- `torch>=2.0.0`
- `huggingface-hub>=0.20.0`
- `tf-keras>=2.15.0`
- `transformers>=4.30.0`

### Первый запуск

При первом запуске модель будет скачана с Hugging Face (около 300MB).
Это займет несколько минут в зависимости от скорости интернета.

После скачивания модель кэшируется локально и не требует повторной загрузки.

### Устройство

- `cpu` - для CPU (по умолчанию)
- `cuda` - для GPU (если доступен CUDA)

### Размерность embeddings

По умолчанию используется полная размерность 768. Можно урезать до:
- 512
- 256
- 128

Для этого нужно изменить код в `rag/vectorstore.py` в `encode_kwargs`.

### Отличие от OpenAI

| Параметр | OpenAI | Hugging Face EmbeddingGemma |
|----------|--------|----------------------------|
| API вызовы | Да (платно) | Нет (локально) |
| Скорость | Зависит от сети | Быстро (локально) |
| Размерность | 1536 (text-embedding-3-small) | 768 (можно урезать) |
| Мультиязычность | Да | Да (100+ языков) |
| Требует токен | OpenAI API key | Hugging Face token |

### Troubleshooting

**Ошибка загрузки модели:**
- Проверьте `HUGGINGFACE_API_TOKEN` в `.env`
- Убедитесь что токен имеет доступ к модели
- Проверьте интернет соединение

**Медленная загрузка:**
- Первая загрузка может занять время
- Модель кэшируется в `~/.cache/huggingface/`

**Нехватка памяти:**
- Используйте `EMBEDDING_DEVICE=cpu`
- Уменьшите размерность embeddings
- Используйте меньший batch size

