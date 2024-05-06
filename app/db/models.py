from app.db.db import db

class Imports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Import {self.hash}>'
    
class Queries(db.Model):
    hash = db.Column(db.Text, primary_key=True)
    result = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'{self.result}'
    
class Repositories(db.Model):
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    primaryLanguage = db.Column(db.Text, nullable=False)
    creationDate = db.Column(db.Text, nullable=False)
    updateDate = db.Column(db.Text, nullable=False)
    pushDate = db.Column(db.Text, nullable=False)
    isArchived = db.Column(db.Boolean, nullable=False)
    archivedAt = db.Column(db.Text, nullable=True)
    isForked = db.Column(db.Boolean, nullable=False)
    isEmpty = db.Column(db.Text, nullable=False)
    isLocked = db.Column(db.Text, nullable=False)
    isDisabled = db.Column(db.Text, nullable=False)
    isTemplate = db.Column(db.Text, nullable=False)
    totalIssueUsers = db.Column(db.Integer, nullable=False)
    totalMentionableUsers = db.Column(db.Integer, nullable=False)
    totalCommitterCount = db.Column(db.Integer, nullable=False)
    totalProjectSize = db.Column(db.Integer, nullable=False)
    totalCommits = db.Column(db.Integer, nullable=False)
    issueCount = db.Column(db.Integer, nullable=False)
    forkCount = db.Column(db.Integer, nullable=False)
    starCount = db.Column(db.Integer, nullable=False)
    watchCount = db.Column(db.Integer, nullable=False)
    branchName = db.Column(db.Text, nullable=False)
    domain = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Repository {self.name}>'
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
  
class Languages(db.Model):
    repoId = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, primary_key=True)
    size = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Language {self.repoId}:{self.name}>'
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Refactorings(db.Model):
    refactoringHash = db.Column(db.Text, primary_key=True,)
    commit = db.Column(db.Text, primary_key=True)
    gituri = db.Column(db.Text)
    repositoryId = db.Column(db.Text, primary_key=True)
    refactoringName = db.Column(db.Text, primary_key=True)
    leftStartLine = db.Column(db.Text)
    leftEndLine = db.Column(db.Text)
    leftStartColumn = db.Column(db.Text)
    leftEndColumn = db.Column(db.Text)
    leftFilePath = db.Column(db.Text)
    leftCodeElementType = db.Column(db.Text)
    leftDescription = db.Column(db.Text)
    leftCodeElement = db.Column(db.Text)
    rightStartLine = db.Column(db.Text)
    rightEndLine = db.Column(db.Text)
    rightStartColumn = db.Column(db.Text)
    rightEndColumn = db.Column(db.Text)
    rightFilePath = db.Column(db.Text)
    rightCodeElementType = db.Column(db.Text)
    rightDescription = db.Column(db.Text)
    rightCodeElement = db.Column(db.Text)
    commitAuthor = db.Column(db.Text)
    commitMessage = db.Column(db.Text)
    commitDate = db.Column(db.Text)

    def __repr__(self):
        return f'<Refactoring {self.refactoringHash}>'
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}