import pytest
from abc import ABC, abstractmethod
from src.infra.di import DIContainer

class IDummyService(ABC):
    @abstractmethod
    def greet(self) -> str:
        pass

class DummyService(IDummyService):
    def greet(self) -> str:
        return "hello"

class NestedService:
    def __init__(self, service: IDummyService) -> None:
        self.service = service

class UnregisteredSimpleClass:
    def __init__(self) -> None:
        self.value = 42

def test_register_and_resolve_concrete() -> None:
    container = DIContainer()
    container.register(IDummyService, DummyService)
    
    # Act
    resolved = container.resolve(IDummyService)
    
    # Assert
    assert isinstance(resolved, DummyService)
    assert resolved.greet() == "hello"

def test_singleton_by_default() -> None:
    container = DIContainer()
    container.register(IDummyService, DummyService)
    
    # Act
    resolved_1 = container.resolve(IDummyService)
    resolved_2 = container.resolve(IDummyService)
    
    # Assert
    assert resolved_1 is resolved_2

def test_transient_when_singleton_is_false() -> None:
    container = DIContainer()
    container.register(IDummyService, DummyService, singleton=False)
    
    # Act
    resolved_1 = container.resolve(IDummyService)
    resolved_2 = container.resolve(IDummyService)
    
    # Assert
    assert resolved_1 is not resolved_2

def test_recursive_dependency_resolution() -> None:
    container = DIContainer()
    container.register(IDummyService, DummyService)
    container.register(NestedService, NestedService)
    
    # Act
    resolved = container.resolve(NestedService)
    
    # Assert
    assert isinstance(resolved, NestedService)
    assert isinstance(resolved.service, DummyService)

def test_auto_resolve_unregistered_concrete_class() -> None:
    container = DIContainer()
    
    # Act
    resolved = container.resolve(UnregisteredSimpleClass)
    
    # Assert
    assert isinstance(resolved, UnregisteredSimpleClass)
    assert resolved.value == 42

def test_error_when_unregistered_interface() -> None:
    container = DIContainer()
    
    # Act & Assert
    with pytest.raises(ValueError, match="is not registered"):
        container.resolve(IDummyService)

def test_di_resolves_cli_controller_with_real_use_cases() -> None:
    from src.infra.cli import CLIController
    from src.app.ports import IConfigProvider, ILibraryRepository, ILoanHistoryRepository
    from src.domain.events import EventDispatcher
    from src.app.use_cases import CheckoutUseCase, ReturnUseCase, ReserveUseCase, WaiveFineUseCase, GenerateReportUseCase

    class DummyConfigProvider:
        def get_max_loans(self) -> int: return 3
        def get_loan_period_days(self) -> int: return 7
        def get_daily_fine_rate(self) -> float: return 2.0
        def get_grace_period_days(self) -> int: return 0
        def get_auto_suspend_overdue_days(self) -> int: return 14
        def get_fine_policy(self) -> dict: return {}

    class DummyRepository:
        pass

    class DummyHistoryRepository:
        pass

    container = DIContainer()
    container.register(IConfigProvider, DummyConfigProvider())
    container.register(ILibraryRepository, DummyRepository())
    container.register(ILoanHistoryRepository, DummyHistoryRepository())
    container.register(EventDispatcher, EventDispatcher)
    
    container.register(CheckoutUseCase, CheckoutUseCase)
    container.register(ReturnUseCase, ReturnUseCase)
    container.register(ReserveUseCase, ReserveUseCase)
    container.register(WaiveFineUseCase, WaiveFineUseCase)
    container.register(GenerateReportUseCase, GenerateReportUseCase)
    container.register(CLIController, CLIController)

    # Act
    controller = container.resolve(CLIController)

    # Assert
    assert isinstance(controller, CLIController)
    assert isinstance(controller.checkout_use_case, CheckoutUseCase)
    assert isinstance(controller.return_use_case, ReturnUseCase)
    assert isinstance(controller.reserve_use_case, ReserveUseCase)
    assert isinstance(controller.waive_fine_use_case, WaiveFineUseCase)
    assert isinstance(controller.generate_report_use_case, GenerateReportUseCase)


# Classes for Circular Dependency Test
class ClassA:
    def __init__(self, dep: 'ClassB') -> None:
        self.dep = dep

class ClassB:
    def __init__(self, dep: 'ClassA') -> None:
        self.dep = dep

# Classes/Interfaces for Unregistered Dependency Test
class IInterfaceY(ABC):
    @abstractmethod
    def run(self) -> None:
        pass

class ClassX:
    def __init__(self, dep: IInterfaceY) -> None:
        self.dep = dep


def test_circular_dependency_error() -> None:
    from src.infra.di import CircularDependencyError
    container = DIContainer()
    container.register(ClassA, ClassA)
    container.register(ClassB, ClassB)

    with pytest.raises(CircularDependencyError) as exc_info:
        container.resolve(ClassA)
    
    assert "Circular dependency detected" in str(exc_info.value)
    assert "ClassA -> ClassB -> ClassA" in str(exc_info.value)


def test_unregistered_dependency_with_path() -> None:
    from src.infra.di import UnregisteredDependencyError
    container = DIContainer()
    container.register(ClassX, ClassX)

    with pytest.raises(UnregisteredDependencyError) as exc_info:
        container.resolve(ClassX)

    assert "is not registered" in str(exc_info.value)
    assert "Resolution path: ClassX -> IInterfaceY" in str(exc_info.value)


def test_duplicate_registration_error() -> None:
    from src.infra.di import DuplicateRegistrationError
    container = DIContainer()
    container.register(IDummyService, DummyService)

    with pytest.raises(DuplicateRegistrationError) as exc_info:
        container.register(IDummyService, DummyService)

    assert "already registered" in str(exc_info.value)


