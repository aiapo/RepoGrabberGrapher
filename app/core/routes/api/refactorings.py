import pandas as pd
from flask import Blueprint
import sqlalchemy
import hashlib
from app.db.models import Queries, Repositories, Refactorings
from app.db.db import db

"""
Create refactorings API blueprint
"""
refactorings_route = Blueprint(
    "refactorings", __name__, template_folder="templates", url_prefix="/refactorings"
)

"""
Refactorings By:

Lists the count of refactorings by a certain metric by the domain in JSON
Save the result in the database too

:param groupBy(str): Domain to group by
    Valid: [all,desktop,mobile,web]
:param countBy(str): Metric to group by
    Valid: [year,type]
"""


@refactorings_route.route("/groupBy/<string:groupBy>/countBy/<string:countBy>")
def refactoringsBy(groupBy, countBy):
    hash = hashlib.md5(("refactoringsBy" + groupBy + countBy).encode()).hexdigest()
    result = db.session.query(Queries.result).filter_by(hash=hash).one_or_none()
    if result != None:
        return result[0]
    else:
        if groupBy == "all":
            if countBy == "year":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        sqlalchemy.func.strftime("%Y", Refactorings.commitDate),
                        sqlalchemy.func.count(
                            sqlalchemy.func.strftime("%Y", Refactorings.commitDate)
                        ),
                    )
                    .group_by(sqlalchemy.func.strftime("%Y", Refactorings.commitDate))
                    .all()
                ]
                r = pd.DataFrame(results, columns=["year", "count"]).to_json(
                    orient="records"
                )
            elif countBy == "type":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        Refactorings.refactoringName,
                        sqlalchemy.func.count(Refactorings.refactoringName),
                    )
                    .group_by(Refactorings.refactoringName)
                    .all()
                ]
                r = pd.DataFrame(results, columns=["type", "count"]).to_json(
                    orient="records"
                )

        elif groupBy == "desktop":
            if countBy == "year":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        sqlalchemy.func.strftime("%Y", Refactorings.commitDate),
                        sqlalchemy.func.count(
                            sqlalchemy.func.strftime("%Y", Refactorings.commitDate)
                        ),
                    )
                    .filter(Repositories.domain == "desktop")
                    .join(Repositories, Repositories.id == Refactorings.repositoryId)
                    .group_by(sqlalchemy.func.strftime("%Y", Refactorings.commitDate))
                    .all()
                ]
                r = pd.DataFrame(results, columns=["year", "count"]).to_json(
                    orient="records"
                )
            elif countBy == "type":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        Refactorings.refactoringName,
                        sqlalchemy.func.count(Refactorings.refactoringName),
                    )
                    .filter(Repositories.domain == "desktop")
                    .join(Repositories, Repositories.id == Refactorings.repositoryId)
                    .group_by(Refactorings.refactoringName)
                    .all()
                ]
                r = pd.DataFrame(results, columns=["type", "count"]).to_json(
                    orient="records"
                )

        elif groupBy == "mobile":
            if countBy == "year":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        sqlalchemy.func.strftime("%Y", Refactorings.commitDate),
                        sqlalchemy.func.count(
                            sqlalchemy.func.strftime("%Y", Refactorings.commitDate)
                        ),
                    )
                    .filter(Repositories.domain == "mobile")
                    .join(Repositories, Repositories.id == Refactorings.repositoryId)
                    .group_by(sqlalchemy.func.strftime("%Y", Refactorings.commitDate))
                    .all()
                ]
                r = pd.DataFrame(results, columns=["year", "count"]).to_json(
                    orient="records"
                )
            elif countBy == "type":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        Refactorings.refactoringName,
                        sqlalchemy.func.count(Refactorings.refactoringName),
                    )
                    .filter(Repositories.domain == "mobile")
                    .join(Repositories, Repositories.id == Refactorings.repositoryId)
                    .group_by(Refactorings.refactoringName)
                    .all()
                ]
                r = pd.DataFrame(results, columns=["type", "count"]).to_json(
                    orient="records"
                )

        elif groupBy == "web":
            if countBy == "year":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        sqlalchemy.func.strftime("%Y", Refactorings.commitDate),
                        sqlalchemy.func.count(
                            sqlalchemy.func.strftime("%Y", Refactorings.commitDate)
                        ),
                    )
                    .filter(Repositories.domain == "web")
                    .join(Repositories, Repositories.id == Refactorings.repositoryId)
                    .group_by(sqlalchemy.func.strftime("%Y", Refactorings.commitDate))
                    .all()
                ]
                r = pd.DataFrame(results, columns=["year", "count"]).to_json(
                    orient="records"
                )
            elif countBy == "type":
                results = [
                    tuple(row)
                    for row in db.session.query(
                        Refactorings.refactoringName,
                        sqlalchemy.func.count(Refactorings.refactoringName),
                    )
                    .filter(Repositories.domain == "web")
                    .join(Repositories, Repositories.id == Refactorings.repositoryId)
                    .group_by(Refactorings.refactoringName)
                    .all()
                ]
                r = pd.DataFrame(results, columns=["type", "count"]).to_json(
                    orient="records"
                )
        else:
            return (
                '{"status":"error","message":"Invalid groupBy or countBy.. Try again."}'
            )

        db.session.add(Queries(hash=hash, result=r))
        db.session.commit()
        return r
