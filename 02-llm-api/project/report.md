1. ![Пример успешного запуска и диалога](reports/0.png)

2. SYSTEM_PROMPT = """Ты — опытный преподаватель программирования на Python.
   Объясняй концепции простым языком с примерами.
   Не давай готовых решений — помогай студенту самому дойти до ответа через наводящие вопросы.
   Поощряй любопытство и эксперименты с кодом.
   Будь терпелив к ошибкам новичков."""
   ![Пример диалога](reports/5.png)
   следует инструкциям
   работает хорошо,

3. чем больше весов тем лучше ответы. Но google gemma 27b отвечает очень хорошо, даже с таким маленьким количеством весов.
4. сначала реализовал обрезание, потом суммаризацию.

## **Ключевые фрагменты кода по суммаризации**:

### **1. Определение объема суммаризации**

```python
messages_to_keep = 5
messages_to_summarize = len(self.conversation_history) - messages_to_keep
```

**Суть**: Фиксированное количество сохраняемых сообщений (5) и расчет, сколько нужно суммаризировать.

### **2. Сохранение системного промпта**

```python
system_message = None
if self.conversation_history and self.conversation_history[0]["role"] == "system":
    system_message = self.conversation_history[0]
    messages_to_summarize -= 1
```

**Суть**: Отдельная обработка системного сообщения, которое должно сохраниться неизменным.

### **3. Проверка необходимости суммаризации**

```python
if messages_to_summarize <= 0:
    return  # Нечего суммаризировать
```

**Суть**: Страховка от ненужной суммаризации.

### **4. Подготовка данных для суммаризации**

```python
start_index = 1 if system_message else 0
end_index = start_index + messages_to_summarize

for msg in self.conversation_history[start_index:end_index]:
    messages_for_summary.append(f"{msg['role']}: {msg['content']}")
```

**Суть**: Извлечение только той части истории, которая будет суммаризироваться.

### **5. Формирование промпта**

```python
summary_prompt = "Кратко резюмируй эту переписку в 2-3 предложениях:\n\n" + "\n".join(messages_for_summary)
```

**Суть**: Шаблон промпта, который гарантирует краткий результат (2-3 предложения).

### **6. Вызов LLM для суммаризации**

```python
response = self.client.chat.completions.create(
    model=self.model_name,
    messages=[{"role": "user", "content": summary_prompt}],
    max_tokens=150  # Ограничение длины резюме
)
summary = response.choices[0].message.content
```

**Суть**: Сам запрос к модели с жестким ограничением токенов.

### **7. Реструктуризация истории**

```python
new_history = []
if system_message:
    new_history.append(system_message)  # Исходный системный промпт

new_history.append({
    "role": "system",
    "content": f"Предыдущая переписка: {summary}"  # Резюме как системное сообщение
})

new_history.extend(self.conversation_history[-messages_to_keep:])  # Последние сообщения
self.conversation_history = new_history
```

**Суть**: Создание новой структуры истории: системный промпт → резюме → свежие сообщения.

### **8. Fallback при ошибке**

```python
except Exception as e:
    # Просто обрезаем историю без суммаризации
    if system_message:
        self.conversation_history = [system_message] + self.conversation_history[-messages_to_keep:]
    else:
        self.conversation_history = self.conversation_history[-messages_to_keep:]
```
