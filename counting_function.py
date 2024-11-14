from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


class CountingObject:
    def __init__(self, salary):
        self.salary = salary  # Исходная зарплата
        self.days_passed = 0  # Количество прошедших дней
        self.total_spent = 0  # Общая сумма потраченных денег
        self.last_spent_amount = 0  # Последняя потраченная сумма

    def daily_budget(self):
        """Расчет текущего дневного бюджета."""
        remaining_amount = self.salary - self.total_spent
        return remaining_amount / (30 - self.days_passed) if (30 - self.days_passed) > 0 else 0

    def spend(self, amount):
        """Метод для учета потраченной суммы."""
        if amount < 0:
            raise ValueError("Сумма не может быть отрицательной.")

        self.total_spent += amount
        self.last_spent_amount = amount
        self.days_passed += 1

    def edit_last_spent(self, new_amount):
        """Метод для редактирования последней потраченной суммы."""
        if new_amount < 0:
            raise ValueError("Сумма не может быть отрицательной.")

        # Обновляем общую сумму потраченных денег
        self.total_spent += (new_amount - self.last_spent_amount)
        self.last_spent_amount = new_amount

    def return_data(self):
        """Строковое представление объекта для удобного вывода информации."""
        return (f"Дней прошло: {self.days_passed}, "
                f"Потрачено: ${self.total_spent:.2f}, "
                f"Дневной бюджет: ${self.daily_budget():.2f}")


# Словарь для хранения объектов CountingObject по ID пользователя
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Введите свою зарплату для начала.")


async def set_salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    try:
        salary = float(context.args[0])
        user_data[user_id] = CountingObject(salary)
        await update.message.reply_text(
            f"Зарплата установлена: ${salary:.2f}. Используйте /spend <сумма> для учета расходов.")
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, введите корректную зарплату.")


async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("Сначала установите свою зарплату с помощью команды /set_salary <сумма>.")
        return

    try:
        amount = float(context.args[0])
        user_data[user_id].spend(amount)
        await update.message.reply_text(user_data[user_id].return_data())
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, введите корректную сумму для расхода.")


async def edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("Сначала установите свою зарплату с помощью команды /set_salary <сумма>.")
        return

    try:
        new_amount = float(context.args[0])
        user_data[user_id].edit_last_spent(new_amount)
        await update.message.reply_text(user_data[user_id].return_data())
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, введите корректную сумму для редактирования.")


def main() -> None:
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = ApplicationBuilder().token("8125694729:AAElye3y_8JUwiZgJXNuIozidQcvHaAcV80").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_salary", set_salary))
    application.add_handler(CommandHandler("spend", spend))
    application.add_handler(CommandHandler("edit_value", edit_value))

    application.run_polling()


if __name__ == '__main__':
    main()

