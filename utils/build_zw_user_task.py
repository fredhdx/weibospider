import sys

sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from db.basic_db import db_session
from db.models import SeedIds
from utils.statistics.tools import get_id_from_zw

for id in get_id_from_zw():
    newone = SeedIds()
    newone.uid = id
    db_session.add(newone)
db_session.commit()
