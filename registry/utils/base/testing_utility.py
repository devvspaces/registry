from rest_framework.serializers import Serializer


class BaseTestHelper:
    def validate_serializer_data(
        self, serializer: Serializer, data: dict, excludes: list = None
    ):
        """Validate the data returned from a serializer is the
        expected response.

        Args:
            serializer (Serializer): Serializer to check
            data (dict): data gotten from serializer
            excludes (list, optional): fields to exclude
            from checking. Defaults to None.
        """
        if excludes is None:
            excludes = []

        excludes_dict = {key: True for key in excludes}

        for key in serializer.get_fields():
            if excludes_dict.get(key) is None:
                assert data.get(key) is not None
