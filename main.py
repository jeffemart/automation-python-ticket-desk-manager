import logging
import telebot
import json
import os

from telebot import types
from utils.logger import configure_logger
from listing.listing import Listing
from subcategory.subcategory import SubcategoryListing
from task.job import JobThread


# Obter o logger configurado
logger = configure_logger()

# Obter o token do ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Obter o ID do Telegram do usuário do ambiente
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

# Verificar se o ID do Telegram do usuário está definido
if not TELEGRAM_USER_ID:
    logger.error(f"'{os.path.basename(__file__)}': Certifique-se de definir a variável de ambiente TELEGRAM_USER_ID no arquivo .env")
    exit()

# Inicializar o bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Criar uma instância da classe Listing
listing_call = Listing()


# Função para verificar o ID do usuário nas mensagens
def is_user_authorized(message):
    # Obter o ID do remetente da mensagem
    user_id = message.from_user.id

    # Verificar se o ID do remetente é igual ao ID do usuário autorizado
    if user_id != int(TELEGRAM_USER_ID):
        logger.warning(f"'{os.path.basename(__file__)}': Usuário não autorizado. ID do usuário: {user_id}")
        bot.send_message(user_id, "Você não está autorizado a usar este bot.")
        return False

    return True


# Comando /start para exibir o menu
@bot.message_handler(commands=["start"])
def start(message):
    # Verificar se o usuário é autorizado
    if not is_user_authorized(message):
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Lista", callback_data="list_ticket")
    item2 = types.InlineKeyboardButton("Categorias", callback_data="update_subcategory")
    item3 = types.InlineKeyboardButton("Iniciar Rotina", callback_data='start_job')
    item4 = types.InlineKeyboardButton("Parar Rotina", callback_data='stop_job')

    markup.add(item1, item2, item3, item4)

    bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)


# Tratamento das opções do menu embutido


@bot.callback_query_handler(func=lambda call: True)
def handle_inline_menu_options(call):
    if call.data == "list_ticket":
        try:
           # Tentar obter a lista de tickets
            recall_listing = Listing()
            get_listing = recall_listing.get_ticket_list()
            bot_list = get_listing

            print(bot_list)

            # Verificar se a lista de tickets não está vazia
            if not bot_list:
                bot.send_message(call.message.chat.id,
                                 "A lista de tickets está vazia.")
                return

            # Lógica para atualizar a lista de subcategorias
            subcategory_instance = SubcategoryListing()
            subcategory_instance.get_subcategory_list()

            # Verificar se o arquivo subcategory_list.json existe
            subcategory_list_file = 'subcategory_list.json'
            if os.path.exists(subcategory_list_file):
                with open(subcategory_list_file, 'r', encoding='utf-8') as json_file:
                    saved_data = json.load(json_file)

                # Lista para armazenar os resultados
                result_list = []

                # Iterar sobre a lista de tickets
                for ticket in bot_list:
                    for item in saved_data:
                        if ticket['CodSubCategoria'] == item['Sequencia']:
                            # Adicionar o resultado à lista
                            result_list.append(
                                (ticket['CodChamado'], item['SubCategoria']))

                # Verificar se a lista de resultados não está vazia
                if not result_list:
                    bot.send_message(
                        call.message.chat.id, "Não foram encontrados resultados correspondentes na lista de subcategorias.")
                else:
                    # Enviar a lista como mensagem
                    formatted_result_list = "\n".join(
                        [f"{code}: {sub}" for code, sub in result_list])
                    bot.send_message(call.message.chat.id,
                                     formatted_result_list)
            else:
                bot.send_message(
                    call.message.chat.id, "O arquivo subcategory_list.json não existe. Execute /update_subcategory para atualizar a lista.")

        except Exception as e:
            # Lidar com exceções que podem ocorrer durante a obtenção da lista de tickets
            bot.send_message(call.message.chat.id,
                             f"Erro ao obter a lista de tickets: {e}")

    elif call.data == "update_subcategory":
        try:
            # Lógica para atualizar a lista de subcategorias
            subcategory_instance = SubcategoryListing()
            subcategory_instance.get_subcategory_list()
            bot.send_message(call.message.chat.id, "Lista de subcategorias atualizada e salva em JSON.",)
        except Exception as e:
            # Lidar com exceções que podem ocorrer durante a atualização da lista de subcategorias
            bot.send_message(call.message.chat.id, f"Erro ao atualizar a lista de subcategorias: {e}")

    elif call.data == 'start_job':
        # Lógica para iniciar o job
        if not hasattr(bot, 'job_thread') or not bot.job_thread.is_alive():
            bot.job_thread = JobThread()
            bot.job_thread.start()
            logging.info(f"{os.path.basename(__file__)}: Job iniciado!")
            bot.send_message(call.message.chat.id, "Job iniciado!")
        else:
            bot.send_message(call.message.chat.id,
                             "O job já está em execução.")
    elif call.data == 'stop_job':
        # Lógica para parar o job
        if hasattr(bot, 'job_thread') and bot.job_thread.is_alive():
            bot.job_thread.stop()
            bot.job_thread.join()
            logging.info(f"{os.path.basename(__file__)}: Job interrompido.")
            bot.send_message(call.message.chat.id, "Job interrompido.")
        else:
            bot.send_message(call.message.chat.id,
                             "O job não está em execução.")

def main():
    # Verificar se todas as variáveis de ambiente necessárias estão definidas
    if not TELEGRAM_BOT_TOKEN:
        logger.error(f"{os.path.basename(__file__)}: Certifique-se de definir a variável de ambiente TELEGRAM_BOT_TOKEN no arquivo .env")
        return

    # Iniciar o bot
    bot.polling()


if __name__ == "__main__":
    main()
