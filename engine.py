import nltk
from parsers import rephrase
import load_helper as dat_loader
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import string
from pattern.text.en import singularize, pluralize
import Levenshtein

# Config
words_excluded = (
"long", "much", "are", "cost", "great", "is", "for", "there", "how", "the", "it", "support", "last", "can", "of",
"have")
mapping = {
    "charge": "battery life",
    "charges": "charge cable",
    "hard": "hard drive",
    "ssd": "SSD",
    "lap": "laptop",
    "wireless": "wireless charging",
    "fingerprint": "fingerprint sensor",
    "face": "face recognition",
    "driver": "driver size",
    "output": "outputs",
    "input": "charge",
}


def cosine_comparision(str1, str2):
    compare_list = [str1.lower(), str2.lower()]
    v = CountVectorizer().fit_transform(compare_list)
    vectors = v.toarray()
    vec1 = vectors[0].reshape(1, -1)
    vec2 = vectors[1].reshape(1, -1)
    return cosine_similarity(vec1, vec2)[0][0]


def get_h_possibility(p_list, lowest=False):
    if lowest:
        seen = {}
        dupes = []
        for x in p_list:
            if x not in seen:
                seen[x] = 1
            else:
                if seen[x] == 1:
                    dupes.append(x)
                seen[x] += 1
        have_dupes = False
        if 0 in dupes:
            dupes.remove(0)
        if len(dupes) != 0:
            have_dupes = True
        h_possibility = min(p_list)
        return {"highest": h_possibility, "dupes": have_dupes, "dupe_list": dupes}
    else:
        seen = {}
        dupes = []
        for x in p_list:
            if x not in seen:
                seen[x] = 1
            else:
                if seen[x] == 1:
                    dupes.append(x)
                seen[x] += 1
        have_dupes = False
        if 0 in dupes:
            dupes.remove(0)
        if len(dupes) != 0:
            have_dupes = True
        h_possibility = max(p_list)
        return {"highest": h_possibility, "dupes": have_dupes, "dupe_list": dupes}


def typo_compare(str1, str2):
    l_dis = Levenshtein.distance(str1.lower(), str2.lower())
    return l_dis


def similar_check_attr(text, attrs):
    for x in attrs:
        cosine_sim = cosine_comparision(x, text)
        # print(f"query: {text}, value: {x}, score: {cosine_sim}")
        if cosine_sim > 0.7:
            return True
        elif cosine_sim == 0:
            l_dis = typo_compare(x, text)
            # print(f"query: {text}, value: {x}, score: {l_dis}")
            if l_dis <= 2:
                return True
    return False


def get_stored_attrs():
    product_list = dat_loader.load_data("Products")["data"]
    attributes = []
    products = []
    product_title = []
    for product in product_list:
        attrs = product.get_attr()["attrs"]
        p_type = product.get_attr()["type"]
        title_tok = product.get_title().split()
        title_tok.remove("Eclectic")
        title = " ".join(title_tok)
        product_title.append(title)
        if p_type == "powerbank":
            mapping["charge"] = "charging"
            mapping["battery"] = "battery life"
        elif p_type == "TV":
            mapping["type"] = ""
        for key in attrs.keys():
            separated = key.replace("_", " ")
            rephrased_sep = rephrase(separated, mapping)
            attributes.append(rephrased_sep)
        p_split = p_type.split("-")
        for x in p_split:
            products.append(x)
    attributes.append("price")
    return {"attributes": attributes, "products": products, "title": product_title}


def is_question(parsed_input):
    word_tokens = nltk.word_tokenize(parsed_input)
    word_tags = nltk.pos_tag(word_tokens)
    q_identifier = ["WP", "WRB", "WDT"]
    q_word_identifier = ["know", "does", "is"]
    for word, tag in word_tags:
        if tag in q_identifier or word.lower() in q_word_identifier:
            return True
    return False


def search_product(query):
    product_list = dat_loader.load_data("Products")["data"]
    query = " ".join(query)
    cosine_sim_list = []
    for product in product_list:
        title = product.get_title().lower()
        title_tok = nltk.word_tokenize(title)
        del title_tok[0]
        title = " ".join(title_tok)
        cosine_sim = cosine_comparision(title, query)
        cosine_sim_list.append(cosine_sim)
        # print(f"Title:{title}, Query:{query.lower()}, score:{cosine_sim}")
    h_p = get_h_possibility(cosine_sim_list)
    if h_p["dupes"]:
        for x in h_p["dupe_list"]:
            if h_p["highest"] == x:
                r_list = []
                for product in product_list:
                    title = product.get_title().lower()
                    title_tok = nltk.word_tokenize(title)
                    del title_tok[0]
                    title = " ".join(title_tok)
                    cosine_sim = cosine_comparision(title, query)
                    if cosine_sim == h_p["highest"]:
                        r_list.append(product)
                p_query = pluralize(query.lower())
                product_title_str = ", ".join([product.get_title() for product in r_list])
                return f"Sorry, you will need to be more specific, we have many {p_query}.\nWe sell {product_title_str}."
    else:
        if h_p["highest"] == 0:
            l_dis_list = []
            for product in product_list:
                title = product.get_title().lower()
                title_tok = nltk.word_tokenize(title)
                del title_tok[0]
                title = " ".join(title_tok)
                l_dis = typo_compare(title, query.lower())
                l_dis_list.append(l_dis)
                # print(f"Title:{title}, Query:{query.lower()}, score:{l_dis}")
            h_p = get_h_possibility(l_dis_list, True)
            if h_p["highest"] > 8:
                return None
            for product in product_list:
                title = product.get_title().lower()
                title_tok = nltk.word_tokenize(title)
                del title_tok[0]
                title = " ".join(title_tok)
                l_dis = typo_compare(title, query.lower())
                if l_dis == h_p["highest"]:
                    return product
        for product in product_list:
            title = product.get_title().lower()
            title_tok = nltk.word_tokenize(title)
            del title_tok[0]
            title = " ".join(title_tok)
            cosine_sim = cosine_comparision(title, query)
            if cosine_sim == h_p["highest"]:
                return product


def identify_product(parsed_input):
    word_tokens = nltk.word_tokenize(parsed_input)
    word_tags = nltk.pos_tag(word_tokens)
    search_query = []
    all_products = get_stored_attrs()["products"]
    all_title = get_stored_attrs()["title"]
    all_attrs = get_stored_attrs()["attributes"]
    for i, word_tag in enumerate(word_tags):
        word, tag = word_tag
        l_dis = typo_compare("Eclectic", word.capitalize())
        if word.capitalize() == "Eclectic" or l_dis < 4:
            try:
                search_query.append(word_tags[i + 1][0])
            except IndexError:
                return None
            counter = 1
            result_save = None
            while True:
                counter += 1
                result = search_product(search_query)
                if isinstance(result, str):
                    try:
                        search_query.append(word_tags[i - 1][0])
                        result_save = result
                    except IndexError:
                        return result
                elif result is not None:
                    return result
                else:
                    try:
                        search_query.append(word_tags[i + counter][0])
                    except IndexError:
                        if result_save is None:
                            return None
                        else:
                            return result_save
        elif similar_check_attr(word, all_products) and word.lower() not in words_excluded and not similar_check_attr(
                word, all_attrs):
            try:
                search_query.append(word)
            except IndexError:
                return None
            counter = 0
            result_save = None
            while True:
                counter += 1
                result = search_product(search_query)
                if isinstance(result, str):
                    try:
                        if word_tags[i - 1][1] not in ("IN", "DT"):
                            search_query.append(word_tags[i - 1][0])
                            result_save = result
                        else:
                            return result
                    except IndexError:
                        return result
                elif result is not None:
                    return result
                else:
                    try:
                        search_query.append(word_tags[i + counter][0])
                    except IndexError:
                        if result_save is None:
                            return None
                        else:
                            return result_save
        elif similar_check_attr(word, all_title) and word.lower() not in words_excluded and not similar_check_attr(word,
                                                                                                                   all_attrs):
            try:
                search_query.append(word)
            except IndexError:
                return None
            counter = 1
            result_save = None
            while True:
                counter += 1
                result = search_product(search_query)
                if isinstance(result, str):
                    try:
                        search_query.append(word_tags[i - 1][0])
                        result_save = result
                    except IndexError:
                        return result
                elif result is not None:
                    return result
                else:
                    try:
                        search_query.append(word_tags[i + counter][0])
                    except IndexError:
                        if result_save is None:
                            return None
                        else:
                            return result_save
        elif word.lower() in ("it", "products"):
            return None
        elif len(word_tags) == i + 1:
            return None


def clean_sentence(sentence):
    stop_words = stopwords.words("English")
    sentence = "".join([word for word in sentence if word not in string.punctuation])
    sentence = sentence.lower()
    sentence = " ".join([word for word in sentence.split() if word not in stop_words])
    words = nltk.word_tokenize(sentence)
    search_query = []
    attr_dat = get_stored_attrs()
    all_attrs = attr_dat["attributes"]
    all_products = attr_dat["products"]
    word_tags = nltk.pos_tag(words)
    new_attrs = []
    for x in all_attrs:
        new_attrs.append(x.lower())
    for i, word_tag in enumerate(word_tags):
        word, tag = word_tag
        l_dis = typo_compare("eclectic", word)
        if word == "eclectic" or l_dis < 4:
            search_query.append(word)
            try:
                search_query.append(words[i + 1])
            except IndexError:
                pass
        elif similar_check_attr(word, all_products) and word.lower() not in words_excluded:
            try:
                if word not in search_query and not similar_check_attr(word, new_attrs):
                    search_query.append(word)
            except IndexError:
                return None
    for x in search_query:
        words.remove(x)
    sentence = " ".join(words)
    return sentence


def gen_reply(ans, product, question):
    product_title = product.get_title()
    if question == "warranty":
        reply = f"The {question} of the {product_title} last for {ans}."
    elif question in "RAM":
        reply = f"The {product_title}'s {question} is {ans}."
    elif question in ("storage hard drive", "storage SSD"):
        word_tok = nltk.word_tokenize(question)
        del word_tok[0]
        rephrased_sep = " ".join(word_tok)
        reply = f"The {rephrased_sep} storage of {product_title} is {ans}."
    elif question == "charge cable":
        reply = f"The charging cable used for the {product_title} is {ans}."
    elif question in ("battery buds", "battery case"):
        word_tok = nltk.word_tokenize(question)
        del word_tok[0]
        rephrased_sep = " ".join(word_tok)
        reply = f"The battery capacity of the {product_title}'s {rephrased_sep} is {ans}."
    elif question == "battery life":
        reply = f"The battery capacity of the {product_title} is {ans}."
    elif question.lower() in ("nfc", "facial recognition", "upgradable storage", "osi", "wireless charging"):
        if ans:
            reply = f"The {product_title} supports {question}."
        else:
            reply = f"The {product_title} does not supports {question}."
    elif singularize(question) == "output":
        reply = f"The {product_title} has {ans} {question}."
    elif question.lower() == "bluetooth":
        reply = f"The {product_title} supports {question} {ans}."
    elif question == "cost price":
        word_tok = nltk.word_tokenize(question)
        del word_tok[0]
        rephrased_sep = "".join(word_tok)
        reply = f"The {rephrased_sep} of {product_title} is ${ans}."
    elif question == "much":
        reply = f"The price of {product_title} is ${ans}."
    elif question.lower() == "sim":
        reply = f"The {product_title} supports {ans} SIM."
    elif question == "fast-charging":
        reply = f"The {product_title} supports {ans} fast charging."
    elif question == "buds battery life":
        word_tok = nltk.word_tokenize(question)
        del word_tok[0]
        rephrased_sep = " ".join(word_tok)
        reply = f"The {rephrased_sep} of the {product_title} is {ans}."
    elif question == "charge":
        reply = f"The {product_title} charges using {ans}."
    elif question.lower() in ("rear camera", "front camera"):
        reply = f"The {product_title} has a {ans} {question}."
    elif question == "fast charging":
        reply = f"The {product_title} supports {ans}."
    elif question.lower() == "storage":
        reply = f"The {product_title} have {ans} internal {question.lower()}."
    elif cosine_comparision(question, "long last"):
        battery_cap = product.get_attr()["attrs"]["battery"]
        battery_cap_int = ""
        for x in battery_cap:
            if x.isnumeric():
                battery_cap_int += x
        product_list = dat_loader.load_data("Products")["data"]
        answer_list = []
        for product in product_list:
            p_attrs = product.get_attr()
            if p_attrs["type"] == "smartphone":
                phone_cap = p_attrs["attrs"].get("battery")
                phone_cap_int = ""
                for x in phone_cap:
                    if x.isnumeric():
                        phone_cap_int += x
                times = int(battery_cap_int) / int(phone_cap_int)
                r = f"{product.get_title()} for {int(times)} time(s)"
                answer_list.append(r)
        ans_str = ", ".join(answer_list)
        reply = f"The powerbank can charge the {ans_str}."
    else:
        reply = f"The {question} of the {product_title} is {ans}."
    return reply


def answer(cleaned_input, product=None, general=True):
    if not general:
        # print(cleaned_input)
        attrs = product.get_attr()["attrs"]
        p_type = product.get_attr()["type"]
        attrs["cost price"] = product.retail_price
        attrs["much"] = product.retail_price
        try:
            attrs["big"] = attrs["display_size"]
        except KeyError:
            pass
        if p_type == "powerbank":
            mapping["charge"] = "charging"
            mapping["battery"] = "battery life"
        elif p_type == "TV":
            mapping["type"] = ""
        cosine_sims = []
        for key in attrs.keys():
            separated = key.replace("_", " ")
            rephrased_sep = rephrase(separated, mapping)
            cosine_sim = cosine_comparision(rephrased_sep, cleaned_input)
            # print(f"key:{rephrased_sep}, question:{cleaned_input}, score:{cosine_sim}")
            cosine_sims.append(cosine_sim)
        if cleaned_input == "long last":
            reply = gen_reply(None, product, cleaned_input)
            return reply
        if "big" in cleaned_input:
            reply = gen_reply(attrs["big"], product, "display size")
            return reply
        h_p = get_h_possibility(cosine_sims)
        h_possibility = h_p["highest"]
        if h_possibility == 0:
            l_dis_list = []
            for key in attrs.keys():
                separated = key.replace("_", " ")
                rephrased_sep = rephrase(separated, mapping)
                l_dis = Levenshtein.distance(rephrased_sep, cleaned_input)
                # print(f"key:{rephrased_sep}, question:{cleaned_input}, score:{l_dis}")
                l_dis_list.append(l_dis)
            h_possibility = min(l_dis_list)
            if h_possibility > 4:
                return "Sorry, I do not understand your question."
            for key in attrs.keys():
                separated = key.replace("_", " ")
                rephrased_sep = rephrase(separated, mapping)
                l_dis = Levenshtein.distance(rephrased_sep, cleaned_input)
                if l_dis == h_possibility:
                    ans = attrs.get(key)
                    reply = gen_reply(ans, product, rephrased_sep)
                    return reply
        for key in attrs.keys():
            separated = key.replace("_", " ")
            rephrased_sep = rephrase(separated, mapping)
            cosine_sim = cosine_comparision(rephrased_sep, cleaned_input)
            if cosine_sim == h_possibility:
                ans = attrs.get(key)
                reply = gen_reply(ans, product, rephrased_sep)
                return reply
