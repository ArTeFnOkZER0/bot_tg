from aiogram.filters import CommandStart, Command
from aiogram.types import Message
# CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
# from smth228.app import keyboards as kb
from smth228.app.middleware import LoggingMiddleware
from aiogram import Router, F, Bot
from aiogram.types import PollAnswer


router = Router()

router.message.middleware(LoggingMiddleware())


class Reg(StatesGroup):
    name = State()
    number = State()


class Poll(StatesGroup):
    question = State()
    options = State()


# Храним только последний опрос
last_poll_id: str | None = None
voters: set[str] = set()


# и
# рассказывать
# анекдот(напиши
# 'расскажи анекдот')
# reply_markup=kb.settings
# reply_markup=kb.main
@router.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("Привет! Я бот и готов к работе 😎. Я умею взаимодействовать с твоими опросами и реакциями "
                         "на сообщения.Если найдешь ошибки жми ----> /report")
# await message.answer("Если найдешь ошибки жми ----> /report")


# @router.message(F.text.lower() == "расскажи анекдот")
# async def joke(message: Message):
#     if message.from_user.username:
#         await message.answer(
#             f'Идут по лесу Дюймовочка, Белоснежка и xуеcoc \nДюймовочка говорит: "Я самая маленькая на Земле. '
#             '\nБелоснежка говорит: "Я самая красивая на свете." \nXуеcoc говорит: "Я больше всех отсосал xyёв." '
#             '\nИдут они, идут, и заходят в Дом Правды. \nДюймовочка в слезах выбегает и говорит: "Ну как так? Я не самая маленькая. Меньше меня мальчик-с-пальчик."'
#             '\n Белоснежка тоже выбегает в слезах и кричит: "О, боже, я не самая красивая. Красивее меня Спящая Красавица."'
#             f'\nВыходит злой хyecос и говорит: "Cyкa, а кто такой @{message.from_user.username}?!"')
#     else:
#         await message.answer(
#             f'Идут по лесу Дюймовочка, Белоснежка и xуеcoc \nДюймовочка говорит: "Я самая маленькая на Земле. '
#             '\nБелоснежка говорит: "Я самая красивая на свете." \nXуеcoc говорит: "Я больше всех отсосал xyёв." '
#             '\nИдут они, идут, и заходят в Дом Правды. \nДюймовочка в слезах выбегает и говорит: "Ну как так? Я не самая маленькая. Меньше меня мальчик-с-пальчик."'
#             '\n Белоснежка тоже выбегает в слезах и кричит: "О, боже, я не самая красивая. Красивее меня Спящая Красавица."'
#             f'\nВыходит злой хyecос и говорит: "Cyкa, а кто такой автор этого бота?!"')


async def is_admin(message: Message, bot: Bot) -> bool:
    """Проверяет, является ли пользователь админом чата"""
    member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    return member.status in ("administrator", "creator")


@router.message(F.text == "/poll")
async def create_poll1(message: Message, state: FSMContext):
    """Создаём опрос"""
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


# @router.message(Command("reg"))
# async def reg_st1(message: Message, state: FSMContext):
#     await state.set_state(Reg.name)
#     await message.answer("Введите ваше имя")
#
#
# @router.message(Reg.name)
# async def reg_st2(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await state.set_state(Reg.number)
#     await message.answer("Введите номер телефона")
#
#
# @router.message(Reg.number)
# async def reg_st3(message: Message, state: FSMContext):
#     await state.update_data(number=message.text)
#     data = await state.get_data()
#     await message.answer(f"Спасибо за регистрацию. \nИмя: {data["name"]} \nНомер: {data["number"]}")
#     await state.clear()
#
#
# @router.message(F.text & ~F.text.startswith("/"))
# async def echo(message: Message):
#     await message.answer(message.text)
#
#
# @router.message(~F.text & ~F.photo)
# async def no_media(message: Message):
#     await message.answer("не шли гифки, стикеры и видео))")


@router.message(Command("report"))
async def report_cmd(message: Message):
    await message.answer("бот работает идельно, не пытайся")


# @router.callback_query(F.data == "aga")
# async def aga(callback: CallbackQuery):
#     await callback.answer("понятно", show_alert=True)
#     await callback.message.edit_text("Зачем нажал?", reply_markup=kb.asd)
#
#
# @router.callback_query(F.data == "zxc")
# async def aga(callback: CallbackQuery):
#     await callback.answer("понятно", show_alert=True)
#
#
# @router.message(F.photo)
# async def get_photo_id(message: Message):
#     await message.answer_photo(photo=message.photo[-1].file_id, caption=f"id фото: {message.photo[-1].file_id}")
