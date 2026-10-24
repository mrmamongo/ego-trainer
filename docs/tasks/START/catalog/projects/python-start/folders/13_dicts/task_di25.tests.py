from ego.testing import case

@case(
    args=([{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}, {'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm4', 'role': 'user', 'text': 'Расскажи про словари', 'tokens': 20}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}], 30),
    expected=[{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}, {'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}],
    description='большое сообщение пропущено, поиск продолжается',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}, {'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm4', 'role': 'user', 'text': 'Расскажи про словари', 'tokens': 20}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}], 16),
    expected=[{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}],
    description='остаток 6: влезает только последнее',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}, {'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm4', 'role': 'user', 'text': 'Расскажи про словари', 'tokens': 20}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}], 10),
    expected=[{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}],
    description='бюджета хватает только на system',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm4', 'role': 'user', 'text': 'Расскажи про словари', 'tokens': 20}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}], 14),
    expected=[{'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}],
    description='без system: m3 и m5',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 100),
    expected=[],
    description='пустая история',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm4', 'role': 'user', 'text': 'Расскажи про словари', 'tokens': 20}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}], 0),
    expected=[],
    description='нулевой бюджет без system',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}, {'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm4', 'role': 'user', 'text': 'Расскажи про словари', 'tokens': 20}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}], 100),
    expected=[{'id': 'm1', 'role': 'system', 'text': 'Ты помощник', 'tokens': 10}, {'id': 'm2', 'role': 'user', 'text': 'Привет', 'tokens': 5}, {'id': 'm3', 'role': 'assistant', 'text': 'Здравствуйте', 'tokens': 8}, {'id': 'm4', 'role': 'user', 'text': 'Расскажи про словари', 'tokens': 20}, {'id': 'm5', 'role': 'assistant', 'text': 'Словарь хранит пары', 'tokens': 6}],
    description='бюджета хватает на всё',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di25_chat_context(messages, budget):
    ...
