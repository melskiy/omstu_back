from typing import BinaryIO
from src.db.db import Session
from src.models.city import City
from src.models.card import Card
from src.models.terminal import Terminal
from src.models.transaction import Transaction
from src.models.operation import Operation
from src.models.operation_type import OperationType
from src.models.terminal_type import TerminalType
from src.models.client import Client
from sqlalchemy import select
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import csv


class DataService:

    async def insert(self, input_file: BinaryIO) -> None:
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(input_file.readline().decode('utf-8')).delimiter
        input_file.seek(0)
        df = pd.read_csv(input_file, sep=str(delimiter))
        operation_res_map = {
            'Успешно': True,
            'Отказ': False
        }
        async with Session() as session:
            for index, row in df.iterrows():
                check = await self.check_rows(row)
                if not check:
                    continue
                transaction_id = row['id_transaction']
                transaction = await (session.get(Transaction, transaction_id))
                if transaction:
                    continue
                transaction_date = datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")
                card_number = row['card']
                if row['passport_valid_to'] == 'бессрочно':
                    passport_valid_to = datetime.now() + relativedelta(years=100)
                else:
                    passport_valid_to = datetime.strptime(row['passport_valid_to'], "%Y-%m-%d")
                card = await session.get(Card, card_number)
                if not card:
                    card = await self.create_card(card_number, row['phone'], row['client'], row['passport'],
                                                  passport_valid_to, row['date_of_birth'], session)
                operation_result = operation_res_map[row['operation_result']]
                q = (select(Operation)
                     .where(Operation.operation_type.has(OperationType.operation_type_name == row['operation_type']))
                     .where(Operation.operation_result == operation_result)
                     .where(Operation.operation_amount == row['amount']))
                result = await session.execute(q)
                operation = result.scalar_one_or_none()
                if not operation:
                    operation = await self.create_operation(row['operation_type'], operation_result, row['amount'],
                                                            session)
                q = (select(Terminal)
                     .where(Terminal.terminal_type
                            .has(TerminalType.terminal_type_name == row['terminal_type']))
                     .where(Terminal.city.has(City.city_name == row['city']))
                     .where(Terminal.terminal_address == row['address']))
                result = await session.execute(q)
                terminal = result.scalar_one_or_none()
                if not terminal:
                    terminal = await self.create_terminal(row['terminal_type'], row['city'], row['address'],
                                                          session)
                transaction = Transaction(transaction_id=transaction_id,
                                          transaction_date=transaction_date,
                                          card_number=card_number,
                                          operation_id=operation.operation_id,
                                          terminal_id=terminal.terminal_id)
                session.add(transaction)
                await session.flush()
            await session.commit()

    @staticmethod
    async def check_rows(row: pd.Series) -> bool:
        if len(str(row['client'])) > 7:
            return False
        if len(str(row['passport'])) > 8:
            return False
        if len(str(row['card'])) > 8:
            return False
        if len(str(row['phone'])) > 8:
            return False
        return True

    async def create_card(self, card_number: str, phone_hashed: str, client_id: str, passport_hashed: str,
                          passport_valid_to: datetime, date_of_birth: datetime, session: Session) -> Card:
        client = await session.get(Client, client_id)
        if not client:
            client = await self.create_client(client_id, passport_hashed, passport_valid_to, date_of_birth, session)
        card = Card(card_number=card_number, phone_hashed=phone_hashed, client_id=client.client_id)
        session.add(card)
        await session.flush()
        return card

    @staticmethod
    async def create_client(client_id: str, passport_hashed: str, passport_valid_to: datetime,
                            date_of_birth: datetime, session: Session) -> Client:
        client = Client(client_id=client_id, passport_hashed=passport_hashed, passport_valid_to=passport_valid_to,
                        date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d"))
        session.add(client)
        await session.flush()
        return client

    async def create_operation(self, operation_type_name: str, operation_result: bool, operation_amount: float,
                               session: Session) -> Operation:
        q = (select(OperationType).where(OperationType.operation_type_name == operation_type_name))
        result = await session.execute(q)
        operation_type = result.scalar_one_or_none()
        if not operation_type:
            operation_type = await self.create_operation_type(operation_type_name, session)

        operation = Operation(operation_type_id=operation_type.operation_type_id,
                              operation_amount=operation_amount,
                              operation_result=operation_result,
                              )
        session.add(operation)
        await session.flush()
        return operation

    @staticmethod
    async def create_operation_type(operation_type_name: str, session: Session) -> OperationType:
        operation_type = OperationType(operation_type_name=operation_type_name)
        session.add(operation_type)
        await session.flush()
        return operation_type

    async def create_terminal(self, terminal_type_name: str, city_name: str, terminal_address: str,
                              session: Session) -> Terminal:
        q = (select(TerminalType).where(TerminalType.terminal_type_name == terminal_type_name))
        result = await session.execute(q)
        terminal_type = result.scalar_one_or_none()
        if not terminal_type:
            terminal_type = await self.create_terminal_type(terminal_type_name, session)
        q = (select(City).where(City.city_name == city_name))
        result = await session.execute(q)
        city = result.scalar_one_or_none()
        if not city:
            city = await self.create_city(city_name, session)
        terminal = Terminal(terminal_type_id=terminal_type.terminal_type_id,
                            city_id=city.city_id,
                            terminal_address=terminal_address)
        session.add(terminal)
        await session.flush()
        return terminal

    @staticmethod
    async def create_terminal_type(terminal_type_name: str, session: Session) -> TerminalType:
        terminal_type = TerminalType(terminal_type_name=terminal_type_name)
        session.add(terminal_type)
        await session.flush()
        return terminal_type

    @staticmethod
    async def create_city(city_name: str, session: Session) -> City:
        city = City(city_name=city_name)
        session.add(city)
        await session.flush()
        return city
