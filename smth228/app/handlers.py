from aiogram.filters import CommandStart, Command
from aiogram.types import Message, MessageReactionUpdated, PollAnswer
# CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
# from smth228.app import keyboards as kb
from smth228.app.middleware import LoggingMiddleware
from aiogram import Router, F, Bot


router = Router()

router.message.middleware(LoggingMiddleware())


class Reg(StatesGroup):
    name = State()
    number = State()


class Poll(StatesGroup):
    question = State()
    options = State()


last_poll_id: str | None = None
voters: set[str] = set()
user_react: set[str] = set()


# и
# рассказывать
# анекдот(напиши
# 'расскажи анекдот')
# reply_markup=kb.settings
# reply_markup=kb.main
@router.message(CommandStart())
async def start_cmd(message: Message):
    if message.chat.type == "private":
        await message.answer("Привет! Я бот и готов к работе 😎. Я умею взаимодействовать с твоими опросами и реакциями "
                             "на сообщения.Если найдешь ошибки жми ----> /report")
# await message.answer("Если найдешь ошибки жми ----> /report")


@router.message_reaction()
async def reaction_handler(event: MessageReactionUpdated):
    user_r = event.user  # кто поставил реакцию
    user_identifier = user_r.username or str(user_r.id)
    if user_identifier not in user_react:
        user_react.add(user_identifier)


@router.message(F.text == "+")
async def plus_handler(message: Message):
    user_plus = message.from_user  # кто поставил реакцию
    user_identifier = user_plus.username or str(user_plus.id)
    if user_identifier not in user_react:
        user_react.add(user_identifier)


@router.message(Command("rstats"))
async def react_stats(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        await message.answer("У вас нет прав на эту команду.")
        return
    await message.answer(f"реакции поставили: {", ".join(user_react)}")
    user_react.clear()


async def is_admin(message: Message, bot: Bot) -> bool:
    """Проверяет, является ли пользователь админом чата"""
    member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    return member.status in ("administrator", "creator")


@router.message(Command("poll"))
async def create_poll1(message: Message, state: FSMContext, bot: Bot):
    """Создаём опрос"""
    if message.chat.type not in ("group", "supergroup"):
        await message.answer("Эта команда работает только в группах")
    if not await is_admin(message, bot):
        await message.answer("У вас нет прав на эту команду.")
        return
    global last_poll_id
    last_poll_id = set()
    await state.set_state(Poll.question)
    await message.answer("Напишите вопрос опроса.")


@router.message(Poll.question)
async def create_poll2(message: Message, state: FSMContext, bot: Bot):
    """Создаём вопрос для опроса"""
    if not await is_admin(message, bot):
        await message.answer("бот не принимает сообщения не от админа")  # убрать потом не забудь
        return
    await state.update_data(question=message.text)
    await state.set_state(Poll.options)
    await message.answer("Напишите варианты ответа через запятую(более 2).")


@router.message(Poll.options)
async def create_poll3(message: Message, state: FSMContext, bot: Bot):
    """Создаём варианты ответа для опроса"""
    global last_poll_id, voters
    if not await is_admin(message, bot):
        await message.answer("бот не принимает сообщения не от админа")  # убрать потом не забудь
        return
    if len(message.text.split(",")) < 2:
        await message.answer("Какую-то хрень ты ввел, через запятую написано же.")
        return
    await state.update_data(options=message.text.split(","))
    poll_data = await state.get_data()
    poll_msg = await bot.send_poll(
        chat_id=message.chat.id,
        question=poll_data["question"],
        options=poll_data["options"],
        is_anonymous=False
    )
    await state.clear()

    last_poll_id = poll_msg.poll.id
    voters = set()


@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):
    """Регистрируем проголосовавших"""
    global voters
    if poll_answer.poll_id == last_poll_id:
        user_identifier = poll_answer.user.username or str(poll_answer.user.id)
        voters.add(user_identifier)


@router.message(F.text == "/stats")
async def poll_stats(message: Message, bot: Bot):
    """Показываем статистику по последнему опросу"""
    global last_poll_id, voters

    if not last_poll_id:
        await message.answer("❌ Нет активного опроса.")
        return

    total = await bot.get_chat_member_count(message.chat.id)
    total -= 1
    not_voted = total - len(voters)

    percent_voted = (len(voters) / total) * 100 if total else 0
    percent_not = (not_voted / total) * 100 if total else 0

    await message.answer(
        f"📊 Статистика:\n\n"
        f"Проголосовали: {len(voters)} человек ({percent_voted:.1f}%) → {", ".join(voters)}\n"
        f"Не проголосовали: {not_voted} человек ({percent_not:.1f}%)")


@router.message(Command("report"))
async def report_cmd(message: Message):
    if message.chat.type == "private":
        await message.answer("бот работает идельно, не пытайся")
