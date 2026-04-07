from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.visual_preference import VisualPreferenceModel


class VisualPreferenceRepository(BaseSQLRepository[VisualPreferenceModel]):

    def __init__(self, session):
        super().__init__(session, VisualPreferenceModel)
