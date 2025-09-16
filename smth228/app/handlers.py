from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from smth228.app import keyboards as kb
from smth228.app.middleware import LoggingMiddleware


router = Router()

router.message.middleware(LoggingMiddleware())


class Reg(StatesGroup):
    name = State()
    number = State()


# и
# рассказывать
# анекдот(напиши
# 'расскажи анекдот')
@router.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("Привет! Я бот и готов к работе 😎. Я умею за тобой повторять и называть айди твоих фото.",
                         reply_markup=kb.settings)
    await message.answer(text="Если найдешь ошибки жми ----> /report", reply_markup=kb.main)


@router.message(F.text.lower() == "расскажи анекдот")
async def joke(message: Message):
    if message.from_user.username:
        await message.answer(
            f'Идут по лесу Дюймовочка, Белоснежка и xуеcoc \nДюймовочка говорит: "Я самая маленькая на Земле. '
            '\nБелоснежка говорит: "Я самая красивая на свете." \nXуеcoc говорит: "Я больше всех отсосал xyёв." '
            '\nИдут они, идут, и заходят в Дом Правды. \nДюймовочка в слезах выбегает и говорит: "Ну как так? Я не самая маленькая. Меньше меня мальчик-с-пальчик."'
            '\n Белоснежка тоже выбегает в слезах и кричит: "О, боже, я не самая красивая. Красивее меня Спящая Красавица."'
            f'\nВыходит злой хyecос и говорит: "Cyкa, а кто такой @{message.from_user.username}?!"')
    else:
        await message.answer(
            f'Идут по лесу Дюймовочка, Белоснежка и xуеcoc \nДюймовочка говорит: "Я самая маленькая на Земле. '
            '\nБелоснежка говорит: "Я самая красивая на свете." \nXуеcoc говорит: "Я больше всех отсосал xyёв." '
            '\nИдут они, идут, и заходят в Дом Правды. \nДюймовочка в слезах выбегает и говорит: "Ну как так? Я не самая маленькая. Меньше меня мальчик-с-пальчик."'
            '\n Белоснежка тоже выбегает в слезах и кричит: "О, боже, я не самая красивая. Красивее меня Спящая Красавица."'
            f'\nВыходит злой хyecос и говорит: "Cyкa, а кто такой автор этого бота?!"')


@router.message(Command("reg"))
async def reg_st1(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer("Введите ваше имя")


@router.message(Reg.name)
async def reg_st2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer("Введите номер телефона")


@router.message(Reg.number)
async def reg_st3(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    data = await state.get_data()
    await message.answer(f"Спасибо за регистрацию. \nИмя: {data["name"]} \nНомер: {data["number"]}")
    await state.clear()


@router.message(F.text & ~F.text.startswith("/"))
async def echo(message: Message):
    await message.answer(message.text)


@router.message(~F.text & ~F.photo)
async def no_media(message: Message):
    await message.answer("не шли гифки, стикеры, фото и видео))")


@router.message(Command("report"))
async def report_cmd(message: Message):
    await message.answer("бот работает идельно, не пытайся")


@router.callback_query(F.data == "aga")
async def aga(callback: CallbackQuery):
    await callback.answer("понятно", show_alert=True)
    await callback.message.edit_text("Зачем нажал?", reply_markup=kb.asd)


@router.callback_query(F.data == "zxc")
async def aga(callback: CallbackQuery):
    await callback.answer("понятно", show_alert=True)


@router.message(F.photo)
async def get_photo_id(message: Message):
    await message.answer_photo(photo="AgACAgIAAxkBAAICCmjJNxwYvTHaNNlZAAHBwFJMT5foSQACSfsxG22lSUojJUFhbHmERwEAAwIAA3kAAzYE", caption=f"id фото: {message.photo[-1].file_id}")