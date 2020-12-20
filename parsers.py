from __future__ import division
import nltk


def size_readable(num, suffix='B'):
  for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
    if abs(num) < 1024.0:
      return "%3.1f%s%s" % (num, unit, suffix)
    num /= 1024.0
  return "%.1f%s%s" % (num, 'Yi', suffix)


def rephrase(sentence, mapping):
  return " ".join([mapping.get(i, i) for i in sentence.split()])


def identify_product(title):
  words = nltk.word_tokenize(title)
  new_words = []
  exclude = ["TWS", "A1", "A2", "B3", "B4", "C5", "C6", "E8", "F9", "TV"]
  cap = False
  for x in words:
    if x[0].isupper() and not cap:
      cap = True
      new_words.append(x)
    elif x[0].isupper() and cap and x not in exclude:
      new_words.append(x.lower())
    else:
      new_words.append(x)
  tags = nltk.pos_tag(new_words)
  noun_def = ["NN", "NNP"]
  while True:
    counter = 0
    values = []
    for word, tag in tags:
      if tag in noun_def:
        counter += 1
        values.append(word)
    if counter == 1:
      return values[0]
    elif len(noun_def) == 1:
      fixed = "-".join(values)
      words = nltk.word_tokenize(title)
      fix_title = [words[0], fixed]
      tags_2 = nltk.pos_tag(fix_title)
      for x in tags_2:
        if x[1] in noun_def:
          return fixed
    else:
      del noun_def[-1]

def find_keywords(tags, attr):
  for a in range(0, len(tags)):
    tag = tags[a]
    if tag[1] in ("VBZ", "VBP", "VBG", "NNS", "VB") and tag[0].lower() not in ("does", "charges"):
      if attr == "display_size":
        try:
          for b in range(a+1, a+6):
            tag2 = tags[b]
            if tag2[1] == "CD":
              for c in range(b+1, b+4):
                tag3 = tags[c]
                if tag3[1] == "NN" or tag3[0] in ("screen", "display"):
                  return tag2[0] + " inch"
        except IndexError:
          continue
      elif attr in ("storage_ssd", "storage_hard"):
        attr = attr.split("_")
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[0] == attr[0]:
              for c in range(b-10, b):
                tag3 = tags[c]
                if tag3[0].lower() == attr[1] and tags[c-1][1] == "CD":
                  return tags[c-1][0]
        except IndexError:
          continue
      elif attr == "battery_lap":
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[0] == "battery" and tags[b+1][0] == "life":
              for c in range(b-5, b):
                tag3 = tags[c]
                if tag3[1] == "CD" and tags[c+1][1] == "NNS":
                  return tag3[0] + " " + tags[c+1][0]
        except IndexError:
          continue
      elif attr == "GPU":
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "NN" and tags[b-1][0] == "graphics" and tags[b-2][1] == "CD" and tags[b-3][1] == "NNP":
              return tags[b-3][0] + " " + tags[b-2][0]
        except IndexError:
          continue
      elif attr in ("output", "input"):
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[0] == attr and attr == "output":
              return tags[b-1][0] + " " + tags[b+1][0]
            elif tag2[0] == attr and attr == "input":
              return tags[b+1][0]
        except IndexError:
          continue
      elif attr == "fast_charge":
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "NNP" and tags[b+1][1] == "NNP" and tags[b+2][1] == "NNP":
              return tag2[0] + " " + tags[b+1][0] + " " + tags[b+2][0] + " " + tags[b+3][0]
        except IndexError:
          continue
      elif attr == "buds_charge":
        attr = attr.split("_")[1]
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[0] == attr and tags[b-1][0] == "single":
              for c in range(b-6, b):
                tag3 = tags[c]
                if tag3[1] == "CD":
                  return tag3[0] + " " + tags[c+1][0]
        except IndexError:
          continue
      elif attr in ("battery_case", "battery_buds"):
        attr = attr.split("_")
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "CD":
              for c in range(b+1, b+4):
                if tags[c][0] == attr[0]:
                  for d in range(c-5, c):
                    if tags[d][0] == attr[1]:
                      return tag2[0]
        except IndexError:
          continue
      elif attr == "driver":
        try:
          for b in range(a+1, a+22):
            tag2 = tags[b]
            if tag2[0] == attr and tags[b-1][1] in ("JJ", "NN"):
              for c in range(b-5, b):
                tag3 = tags[c]
                if tag3[1] == "CD":
                  return tag3[0]
        except IndexError:
          continue
      elif attr == "driver_type":
        attr = attr.split("_")[0]
        try:
          for b in range(a+1, a+22):
            tag2 = tags[b]
            if tag2[0] == attr and tags[b-1][1] in ("JJ", "NN") and tags[b-2][1] in ("JJ", "NN"):
              return tags[b-2][0] + " " + tags[b-1][0]
            elif tag2[0] == attr and tags[b-1][1] in ("JJ", "NN"):
              return tags[b-1][0]
        except IndexError:
          continue
      elif attr == "upgradable_storage":
        attr = attr.split("_")[0]
        try:
          for b in range(a+1, a+22):
            tag2 = tags[b]
            if tag2[0] == attr and tags[b-1][0] in ("no", "not"):
              return False
            elif tag2[0] == attr and tags[b-1][0] not in ("no", "not"):
              return True
        except IndexError:
          continue
      elif attr == "display_type":
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "NNP" and tags[b+1][0].lower() == "screen":
              return tag2[0]
        except IndexError:
          continue
      elif attr == "Bluetooth":
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "NNP" and tag2[0] == attr:
              tag3 = tags[b+1]
              if tag3[0][:1].lower() == "v":
                return tag3[0]
        except IndexError:
          continue
      elif attr == "SIM":
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "NNP" and tag2[0] == attr:
              if tags[b-1][0] == "dual" and tags[b-2][0] not in ("no", "not"):
                return "dual"
              elif tags[b-1][0] == "dual" and tags[b-2][0] in ("no", "not"):
                return "single"
              else:
                return "single"
        except IndexError:
          continue
      elif attr == "Optical Image Stabilization":
        attr = attr.split(" ")
        con_s = 0
        neg = False
        try:
          for b in range(a+1, a+20):
            if con_s == 3 and not neg:
              return True
            elif con_s == 3 and neg:
              return False
            tag2 = tags[b]
            if tag2[0] in attr and tag2[1] == "NNP":
              con_s += 1
              if tags[b-1][0] in ("no", "not") and tags[b-1][1] == "DT":
                neg = True
        except IndexError:
          continue
      elif attr in ("battery", "fast-charging", "RAM", "storage"):
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "CD":
              for c in range(b+1, b+4):
                if tags[c][0] == attr:
                  return tag2[0]
        except IndexError:
          continue
      elif attr == "charges":
        try:
          for b in range(a-2, a):
            tag2 = tags[b]
            if tag2[0] == attr:
              for c in range(a+1, a+6):
                tag3 = tags[c]
                if tag3[1] == "NNP":
                  return tag3[0] + " " + tags[c+1][0]
        except IndexError:
          continue
      elif attr == "warranty" and tags[a+1][1] == "IN":
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] == "CD":
              for c in range(b+1, b+3):
                tag3 = tags[c]
                if tag3[0] == attr:
                  return tag2[0] + " " + tags[b+1][0]
        except IndexError:
          continue
      elif attr == "rear_camera" or attr == "front_camera":
        try:
          attr = attr.split("_")[0]
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[0] in attr and tags[b + 1][1] == "NN":
              for c in range(b-3, b):
                tag3 = tags[c]
                if tag3[1] == "CD" and tags[c + 1][0] == "MP":
                  return tag3[0] + " MP"
        except IndexError:
          continue
      else:
        try:
          for b in range(a+1, a+20):
            tag2 = tags[b]
            if tag2[1] in ("NNP", "NN", "JJ") and tag2[0] == attr and tags[a-1][0].lower() in ("no", "not"):
              return False
            elif tag2[1] in ("NNP", "NN", "JJ") and tag2[0] == attr and tags[a-1][0].lower() not in ("no", "not"):
              return True
        except IndexError:
          continue



def extract_info(sentences, attr_type, mapping):
  attr_maps = {
    "smartphone": ["NFC", "display_size", "charges", "wireless", "battery", "RAM", "fast-charging", "storage",
                   "upgradable_storage", "front_camera", "rear_camera", "OSI", "SIM",
                   "fingerprint", "face", "warranty", "bluetooth"],
    "TV": ["display_size", "warranty", "display_type"],
    "earbuds": ["warranty", "driver_type", "battery_case", "battery_buds",
                "buds_charge", "charges"],
    "powerbank": ["battery", "warranty", "output", "input", "fast_charge"],
    "mouse": ["warranty"],
    "headphone": ["driver", "driver_type", "warranty"],
    "smartwatch": ["warranty", "NFC", "bluetooth", "battery", "RAM", "storage",
                   "SIM"],
    "camera": ["warranty", "battery"],
    "lamp": ["warranty"],
    "gaming-laptop": ["storage_hard", "storage_ssd", "GPU", "battery_lap", "RAM", "display_size", "warranty"],
    "washing-machine": ["warranty"],
    "vacuum-machine": ["warranty"],
    "toaster": ["warranty"],
    "induction-cooker": ["warranty"],
    "air-conditioner": ["warranty"],
    "standing-fan": ["warranty"],
    "hairdryer": ["warranty"],
    "printer": ["warranty"],
    "printer-ink": [],
  }
  dat = {}
  try:
    attrs = attr_maps[attr_type]
  except KeyError:
    attrs = []
  # attrs = []
  for sentence in sentences:
    tags = nltk.pos_tag(nltk.word_tokenize(rephrase(sentence, mapping)))
    for x in attrs:
      if dat.get(x) is None:
        attr = rephrase(x, mapping)
        dat[x] = find_keywords(tags, attr)
  for x in attrs:
    if dat.get(x) is None:
      dat[x] = False
  return dat