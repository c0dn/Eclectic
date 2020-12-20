import load_helper as dat_loader
from users import Staff

def is_authenticated(request):
  session_id = request.cookies.get("sessionID")
  if session_id is None:
    return False
  sessions = dat_loader.load_data("Session")["data"]
  for x in sessions:
    if x.get_id() == session_id and x.check():
      return True

def get_user(request):
  sessions = dat_loader.load_data("Session")["data"]
  user_id = int(request.cookies.get("userID"))
  session_id = request.cookies.get("sessionID")
  user_list = dat_loader.load_data("Users")["data"]
  for session in sessions:
    if session.get_id() == session_id and user_id == session.get_user_id():
      for user in user_list:
        if user.get_id() == session.get_user_id():
          return user


def refresh_session(request):
  sessions = dat_loader.load_data("Session")["data"]
  session_id = request.cookies.get("sessionID")
  for session in sessions:
    if session.get_id() == session_id:
      session.refresh()
  dat_loader.write_data("Session", sessions, False)

def session_end(request):
  sessions = dat_loader.load_data("Session")["data"]
  session_id = request.cookies.get("sessionID")
  for session in sessions:
    if session.get_id() == session_id:
      session.logout()
  dat_loader.write_data("Session", sessions, False)

def is_staff(request):
  sessions = dat_loader.load_data("Session")["data"]
  user_id = int(request.cookies.get("userID"))
  session_id = request.cookies.get("sessionID")
  for session in sessions:
    if session.get_id() == session_id and user_id == session.get_user_id():
      user = session.get_user()
      if isinstance(user, Staff):
        return True
      else:
        return False