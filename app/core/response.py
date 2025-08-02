from math import ceil
from typing import Any, Optional, List
from fastapi import Request
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from http import HTTPStatus


class Pagination(BaseModel):
    page: int
    per_page: int
    total_items: int
    total_pages: int = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.per_page > 0:
            self.total_pages = ceil(self.total_items / self.per_page)
        else:
            self.total_pages = 0

    def paging_data(self, data: List[Any]) -> List[Any]:
        start_index = (self.page - 1) * self.per_page
        end_index = start_index + self.per_page

        # Get the paginated items
        return data[start_index:end_index]


class APIResponse(BaseModel):
    """
    The class which represent the standard basemodel of response model.
    Needed this to display the response model for openAPI.
    """

    status: bool = True
    code: int = HTTPStatus.OK
    message: str = ""
    pagination: Optional[Pagination] = None
    error: Optional[Any] = None
    data: Optional[Any] = None  # Optional field for additional data


class Response(JSONResponse):
    """
    The standard response class

    Inside it will use the APIResponse class just to make sure the response model is similar with the openAPI response model
    """

    def __init__(
        self,
        status: bool = True,
        code: int = HTTPStatus.OK,
        message: str = "",
        headers: Optional[dict] = None,
        pagination: Optional[Pagination] = None,
        error: Optional[Any] = None,
        data: Optional[Any] = None,
        api_response_model: Optional[APIResponse] = None,
    ):
        if not api_response_model:
            api_response_model = APIResponse(
                status=status, code=code, message=message, pagination=pagination, error=error, data=data
            )
        if headers is None:
            super().__init__(content=api_response_model.model_dump(), status_code=api_response_model.code)
        else:
            super().__init__(
                content=api_response_model.model_dump(), status_code=api_response_model.code, headers=headers
            )


class BadRequestErrorResponse(BaseModel):
    """
    The class which represent the standard basemodel of error response model for code 422.
    Needed this to display the response model for openAPI.
    """

    status: bool = False
    code: int = HTTPStatus.BAD_REQUEST
    message: str = Field(default="Order not found, please check your input order id")
    pagination: Pagination = Field(default=None)
    error: Optional[Any] = Field(default=None)
    data: Optional[Any] = None  # Optional field for additional data


class InternalServerErrorResponse(BaseModel):
    """
    The class which represent the standard basemodel of error response model for code 500.
    Needed this to display the response model for openAPI.
    """

    status: bool = False
    code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    message: str = Field(default="")
    pagination: Pagination = Field(default=None)
    error: Optional[Any] = Field(default=None)
    data: Optional[Any] = None  # Optional field for additional data


class UnauthorizedErrorResponse(BaseModel):
    """
    The class which represent the standard basemodel of error response model for code 401.
    Needed this to display the response model for openAPI.
    """

    status: bool = False
    code: int = HTTPStatus.UNAUTHORIZED
    message: str = Field(default="", examples=["Unauthorized access"])
    pagination: Pagination = Field(default=None)
    error: Optional[Any] = Field(default=None, examples=["Invalid Token"])
    data: Optional[Any] = None  # Optional field for additional data


class ValidationErrorResponse(BaseModel):
    """
    The class which represent the standard basemodel of error response model for code 422.
    Needed this to display the response model for openAPI.
    """

    status: bool = False
    code: int = HTTPStatus.UNPROCESSABLE_ENTITY
    message: str = Field(default="", examples=["Error Message"])
    pagination: Pagination = Field(default=None)
    error: Optional[Any] = Field(default=None, examples=["Ex:body|quantity|Input should be a valid integer|ABC"])
    data: Optional[Any] = None  # Optional field for additional data
