from abc import ABCMeta, abstractmethod
from typing import Optional, Union

from tqdm import tqdm


class BaseProgressReporter(metaclass=ABCMeta):
    @abstractmethod
    def set_attr(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, prgs: Union[float, int]) -> None:
        raise NotImplementedError

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        raise NotImplementedError


class TqdmProgressReporter(BaseProgressReporter):
    def __init__(self, tqdm_inst: Optional[tqdm] = None) -> None:
        if tqdm_inst is None:
            tqdm_inst = tqdm()
        self._tqdm_inst = tqdm_inst

    def update(self, prgs: Union[float, int]) -> None:
        self._tqdm_inst.update(prgs)

    def set_attr(self, **kwargs) -> None:
        for attr, val in kwargs.items():
            setattr(self._tqdm_inst, attr, val)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._tqdm_inst.close()
        return False
