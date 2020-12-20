import asyncio
import websockets
import nltk
from parsers import rephrase
from engine import is_question, identify_product, answer, clean_sentence, get_stored_attrs
import random
from pattern.text.en import pluralize
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

mappings = {
  "HD": "hard drive",
}

async def main(websocket, path):
  await websocket.send("Hello, My name is Zoro and I am here to help! :)")
  print("> Hello, My name is Zoro and I am here to help! :)")
  context = None
  while True:
    try:
      user_input = await websocket.recv()
      print(f"< {user_input}")
    except ConnectionClosedError:
      print("< Client close connection")
      break
    except ConnectionClosedOK:
      print("< Client close connection")
      break
    user_input_tok = nltk.word_tokenize(user_input)
    skip_logic = False
    exit_loop = False
    for word in user_input_tok:
      if word.lower() in ("thank", "you", "thanks"):
        await websocket.send("You are welcome, If you need further assistance I will be here to help!")
        print("> You are welcome, If you need further assistance I will be here to help!")
        skip_logic = True
        exit_loop = True
        break
      elif word.lower() in ("hello", "hi"):
        await websocket.send("Hi, good day to you!")
        print("> Hi, good day to you!")
        await websocket.send("How may I help you today?")
        print("> How may I help you today?")
        skip_logic = True
        break
    if skip_logic and exit_loop:
      break
    elif skip_logic:
      continue
    parsed_input = rephrase(user_input, mappings)
    if is_question(parsed_input):
      product = identify_product(parsed_input)
      if isinstance(product, str):
        line_split = product.split(".")
        line1 = line_split[0] + "."
        line2 = line_split[1] + "."
        await websocket.send(line1)
        print(f"> {line1}")
        await websocket.send(line2)
        print(f"> {line2}")
        context = None
      elif product is not None:
        context = product
        cleaned = clean_sentence(parsed_input)
        ans = answer(cleaned, product, general=False)
        await websocket.send(ans)
        print(f"> {ans}")
      elif product is None and context is not None:
        for word, tag in nltk.pos_tag(nltk.word_tokenize(parsed_input)):
          if tag == "PRP":
            cleaned = clean_sentence(parsed_input)
            ans = answer(cleaned, context, general=False)
            await websocket.send(ans)
            print(f"> {ans}")
      # print(cleaned)
      elif product is None and context is None:
        if "products" in nltk.word_tokenize(parsed_input):
          products_type = get_stored_attrs()["products"]
          seen = {}
          dupes = []
          for x in products_type:
            if x not in seen:
              seen[x] = 1
            else:
              if seen[x] == 1:
                dupes.append(x)
              seen[x] += 1
          for x in dupes:
            products_type.remove(x)
          for i, x in enumerate(products_type):
            products_type[i] = pluralize(x)
          products_str = ", ".join(products_type)
          products = get_stored_attrs()["title"]
          random_product = []
          for x in range(0, 3):
            random_product.append(random.choice(products))
          products_t_str = ", ".join(random_product)
          await websocket.send(f"We sell {products_str}")
          print(f"> We sell {products_str}")
          await websocket.send(f"Some of the products we sell are {products_t_str}.")
          print(f"> Some of the products we sell are {products_t_str}.")
        else:
          await websocket.send("Sorry I do not understand your question")
          print("> Sorry I do not understand your question")
          await websocket.send("You may contact our support team by opening a new request for assistance")
          print("> You may contact our support team by opening a new request for assistance")
      else:
        await websocket.send("Sorry, I can only answer questions regarding the products we sell.")
        print("> Sorry, I can only answer questions regarding the products we sell.")
        await websocket.send("You may contact our support team by opening a new request for assistance")
        print("> You may contact our support team by opening a new request for assistance")
    else:
      await websocket.send("Sorry, I can only answer questions regarding the products we sell.")
      print("> Sorry, I can only answer questions regarding the products we sell.")
      await websocket.send("You may contact our support team by opening a new request for assistance")
      print("> You may contact our support team by opening a new request for assistance")

host = "localhost"
port = 8000

start_server = websockets.serve(main, host, port)

asyncio.get_event_loop().run_until_complete(start_server)
print(f"Server started on {host}:{port}")
print(f"URI: ws://{host}:{port}\n")
print("LOG")
asyncio.get_event_loop().run_forever()