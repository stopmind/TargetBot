from random import randint

from aiogram.filters import Command
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel, Field
from typing_extensions import ClassVar
from service import AService, ServicesController

class SapperCell(BaseModel):
    is_bomb: bool
    with_flag: bool
    number: int
    is_unknown: bool

    def to_emoji(self) -> str:
        if self.with_flag:   return "🚩"
        if self.is_unknown:  return "⬛"
        if self.is_bomb:     return "💣"
        if self.number == 0: return "🟦"

        return str(self.number)

class SapperGame(BaseModel):
    game_map: list[SapperCell]
    flags_count: int
    use_flags: bool
    message_id: int
    chat_id: int
    is_finished: bool

def sapper_get_buttons(game: SapperGame) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = MiniGamesService.SAPPER_WIDTH
    for i in range(0, MiniGamesService.SAPPER_WIDTH * MiniGamesService.SAPPER_HEIGHT):
        builder.add(InlineKeyboardButton(
            text=game.game_map[i].to_emoji(),
            callback_data=f"sapper_cell_{i}"
        ))

    if game.use_flags:
        builder.add(InlineKeyboardButton(
            text=f"✅🚩Помечать",
            callback_data=f"sapper_set_flag"
        ))

        builder.add(InlineKeyboardButton(
            text=f"⛏Вскапывать",
            callback_data=f"sapper_set_dig"
        ))
    else:
        builder.add(InlineKeyboardButton(
            text=f"🚩Помечать",
            callback_data=f"sapper_set_flag"
        ))

        builder.add(InlineKeyboardButton(
            text=f"✅⛏Вскапывать",
            callback_data=f"sapper_set_dig"
        ))

    return builder.as_markup()

def gen_map() -> list[SapperCell]:
    result = []

    size = MiniGamesService.SAPPER_WIDTH * MiniGamesService.SAPPER_HEIGHT

    for _ in range(0, size):
        result.append(SapperCell(
            is_bomb=False,
            with_flag=False,
            number=0,
            is_unknown=True
        ))

    bombs = []

    while len(bombs) < MiniGamesService.SAPPER_BOMBS:
        pos = randint(0, size - 1)
        if not pos in bombs:
            bombs.append(pos)

    for pos in bombs:
        result[pos].is_bomb = True
        x = pos % MiniGamesService.SAPPER_WIDTH
        y = int(pos / MiniGamesService.SAPPER_WIDTH)

        around = [
            (x-1, y-1), (x, y-1), (x+1, y-1),
            (x-1, y),             (x+1, y),
            (x-1, y+1), (x, y+1), (x+1, y+1)
        ]

        for around_pos in around:
            if (0 <= around_pos[0] < MiniGamesService.SAPPER_WIDTH) and (0 <= around_pos[1] < MiniGamesService.SAPPER_HEIGHT):
                result[around_pos[0] + around_pos[1] * MiniGamesService.SAPPER_WIDTH].number += 1


    return result

lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],

    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],

    [0, 4, 8],
    [2, 4, 6]
]

class TicTacToeGame(BaseModel):
    PLAYER_NONE: ClassVar[int] = 0
    PLAYER_USER: ClassVar[int] = 1
    PLAYER_BOT:  ClassVar[int] = 2

    game_map: list[int]
    is_finished: bool
    chat_id: int
    message_id: int
    winner: int

    def get_buttons(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.max_width = 3

        for i in range(0, 9):
            builder.add(InlineKeyboardButton(
                text={
                    TicTacToeGame.PLAYER_NONE: "▫",
                    TicTacToeGame.PLAYER_USER: "❌",
                    TicTacToeGame.PLAYER_BOT:  "⭕"
                }[self.game_map[i]],
                callback_data=f"tictactoe_cell_{i}"
            ))

        return builder.as_markup()

    def check_win(self, player: int) -> bool:
        for line in lines:
            full = True
            for pos in line:
                full = full and self.game_map[pos] == player

            if full:
                self.is_finished = True
                self.winner = player
                return True

        return False

    def check_full(self) -> bool:
        for cell in self.game_map:
            if cell == TicTacToeGame.PLAYER_NONE:
                return False

        self.is_finished = True
        self.winner = TicTacToeGame.PLAYER_NONE
        return True


def bot_check_lines(game_map: list[int], target: int) -> bool:
    for line in lines:
        free = -1
        for pos in line:
            if game_map[pos] == TicTacToeGame.PLAYER_NONE:
                if free == -1:
                    free = pos
                else:
                    free = -1
                    break
            elif game_map[pos] != target:
                free = -1
                break

        if free != -1:
            game_map[free] = TicTacToeGame.PLAYER_BOT
            return True
    return False

def bot_do_step(game_map: list[int]):
    if bot_check_lines(game_map, TicTacToeGame.PLAYER_BOT): return
    if bot_check_lines(game_map, TicTacToeGame.PLAYER_USER): return

    pos = randint(0, 8)
    while game_map[pos] != TicTacToeGame.PLAYER_NONE:
        pos = randint(0, 8)

    game_map[pos] = TicTacToeGame.PLAYER_BOT

class MiniGamesService(AService):
    SAPPER_WIDTH:  ClassVar[int] = 8
    SAPPER_HEIGHT: ClassVar[int] = 8
    SAPPER_BOMBS:  ClassVar[int] = 5

    sapper_games: dict[int, SapperGame] = Field({}, init_var=False)
    tictactoe_games: dict[int, SapperGame] = Field({}, init_var=False)

    def get_sapper_game(self, chat_id: int) -> SapperGame | None:
        if chat_id in self.sapper_games:
            result = self.sapper_games[chat_id]
            if result.is_finished:
                return None
            return result
        return None

    def new_sapper_game(self, chat_id: int) -> SapperGame:
        game = SapperGame(
            game_map=gen_map(),
            flags_count=0,
            use_flags=False,
            chat_id=chat_id,
            message_id=0,
            is_finished=False
        )

        self.sapper_games[chat_id] = game

        return game

    def get_tictactoe_game(self, chat_id: int) -> TicTacToeGame | None:
        if chat_id in self.tictactoe_games:
            result = self.tictactoe_games[chat_id]
            if result.is_finished:
                return None
            return result
        return None

    def new_tictactoe_game(self, chat_id: int) -> TicTacToeGame:
        game = TicTacToeGame(
            game_map=[TicTacToeGame.PLAYER_NONE for _ in range(0, 9)],
            chat_id=chat_id,
            is_finished=False,
            message_id=0,
            winner=0
        )

        self.tictactoe_games[chat_id] = game

        return game

    def init(self, bot: Bot, dispatcher: Dispatcher, controller: ServicesController):

        @dispatcher.message(Command("sapper"))
        async def cmd_sapper(message: Message):
            game = self.new_sapper_game(message.chat.id)
            game.message_id = (await bot.send_message(
                text=f"Бомбы: {game.flags_count}/{MiniGamesService.SAPPER_BOMBS}",
                reply_markup=sapper_get_buttons(game),
                chat_id=message.chat.id
            )).message_id

        async def update_sapper_message(game: SapperGame):
            state = ""

            if game.is_finished:
                state = "Завершено"

            await bot.edit_message_text(
                f"Бомбы: {game.flags_count}/{MiniGamesService.SAPPER_BOMBS}. {state}",
                reply_markup=sapper_get_buttons(game),
                message_id=game.message_id,
                chat_id=game.chat_id
            )

        @dispatcher.callback_query(lambda a: a.data.startswith("sapper_set_"))
        async def callback_sapper_set(callback: CallbackQuery):
            game = self.get_sapper_game(callback.message.chat.id)
            if game is None: return await callback.answer()

            game.use_flags = callback.data.endswith("flag")
            await update_sapper_message(game)
            await callback.answer()

        @dispatcher.callback_query(lambda a: a.data.startswith("sapper_cell_"))
        async def callback_sapper_cell(callback: CallbackQuery):
            game = self.get_sapper_game(callback.message.chat.id)
            if game is None: return await callback.answer()

            cell_pos = int(callback.data.replace("sapper_cell_", ""))
            cell = game.game_map[cell_pos]
            changed = False

            if game.use_flags:
                if not (not cell.with_flag and game.flags_count == MiniGamesService.SAPPER_BOMBS) and cell.is_unknown:
                    cell.with_flag = not cell.with_flag
                    if cell.with_flag:
                        game.flags_count += 1
                    else:
                        game.flags_count -= 1
                    changed = True
            else:
                if cell.is_unknown and not cell.with_flag:
                    cell_positions = [cell_pos]

                    i = 0
                    while i < len(cell_positions):
                        current_cell_position = cell_positions[i]
                        current_cell = game.game_map[current_cell_position]
                        i += 1

                        if not current_cell.is_unknown or current_cell.with_flag:
                            continue

                        current_cell.is_unknown = False

                        if current_cell.number != 0 or current_cell.is_bomb:
                            continue

                        x = current_cell_position % MiniGamesService.SAPPER_WIDTH
                        y = int(current_cell_position / MiniGamesService.SAPPER_WIDTH)

                        around = [
                            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                            (x - 1, y),                 (x + 1, y),
                            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
                        ]

                        for around_pos in around:
                            if (0 <= around_pos[0] < MiniGamesService.SAPPER_WIDTH) and (0 <= around_pos[1] < MiniGamesService.SAPPER_HEIGHT):
                                cell_positions.append(around_pos[1] * MiniGamesService.SAPPER_WIDTH + around_pos[0])

                    changed = True


            if changed:
                full = True
                for i in range(0, MiniGamesService.SAPPER_WIDTH * MiniGamesService.SAPPER_HEIGHT):
                    cell = game.game_map[i]
                    if not cell.is_unknown and cell.is_bomb:
                        game.is_finished = True
                        break

                    if cell.is_unknown and not cell.with_flag:
                        full = False

                game.is_finished = game.is_finished or full

                await update_sapper_message(game)

            await callback.answer()

        @dispatcher.message(Command("tictactoe"))
        async def cmd_tictactoe(message: Message):
            game = self.new_tictactoe_game(message.chat.id)
            game.message_id = (await bot.send_message(
                text="В процессе",
                chat_id=message.chat.id,
                reply_markup=game.get_buttons()
            )).message_id

        async def update_tictactoe_message(game: TicTacToeGame):
            text = "В процессе"

            if game.is_finished:
                text = {
                    TicTacToeGame.PLAYER_NONE: "Ничья.",
                    TicTacToeGame.PLAYER_USER: "Победа игрока.",
                    TicTacToeGame.PLAYER_BOT:  "Победа бота."
                }[game.winner]

            await bot.edit_message_text(
                text,
                reply_markup=game.get_buttons(),
                chat_id=game.chat_id,
                message_id=game.message_id
            )

        @dispatcher.callback_query(lambda a: a.data.startswith("tictactoe_cell_"))
        async def callback_tictactoe_cell(callback: CallbackQuery):
            game = self.get_tictactoe_game(callback.message.chat.id)
            if game is None: return await callback.answer()

            cell_pos = int(callback.data.replace("tictactoe_cell_", ""))
            if game.game_map[cell_pos] != TicTacToeGame.PLAYER_NONE: return await callback.answer()

            while True:
                game.game_map[cell_pos] = TicTacToeGame.PLAYER_USER
                if game.check_win(TicTacToeGame.PLAYER_USER): break
                if game.check_full(): break

                bot_do_step(game.game_map)
                game.check_win(TicTacToeGame.PLAYER_BOT)
                break

            await update_tictactoe_message(game)
            await callback.answer()
