from sqlalchemy import delete, select, update, insert
from sqlalchemy.orm import joinedload

# exceptions 
from sqlalchemy.exc import NoResultFound
import datetime

from .engine import session_maker
from .models import User, UserTrainings, FinishedUserTraining, UserStats

# *user

USER_OPTIONS = (joinedload(User.trainings), joinedload(User.finished_trainings), joinedload(User.stats))
async def create_user(user_id, user_name, lang, db_session=None) -> User:
    if db_session == None:
        db_session = session_maker()

    async with db_session:
        all_ids = [u.id for u in await get_all_users(db_session)]

        if user_id not in all_ids:
            status = "user"
            if user_id == 859261869:
                status = "admin"

            new_user = User(
                id=user_id, 
                name=user_name,
                status=status,
                lang=lang
            )
            db_session.add(new_user)
            await db_session.commit()

            return new_user
        
async def get_user(user_id, db_session=None) -> User | None:
    if db_session == None:
        db_session = session_maker()

    async with db_session:
        query = select(User).where(User.id == user_id).options(*USER_OPTIONS)
        data = await db_session.execute(query)
        
        try:
            return data.unique().scalars().one()
        except NoResultFound:
            return None
        
async def update_user(user_id, data, db_session=None) -> User:
    if db_session == None:
        db_session = session_maker()

    async with db_session:
        query = update(User).where(User.id == user_id).values(**data)
        await db_session.execute(query)
        await db_session.commit()

        data = await db_session.get(User, user_id, options=USER_OPTIONS)
        return data
        
async def delete_user(user_id, db_session=None):
    if db_session == None:
        db_session = session_maker()

    async with db_session:
        user = await db_session.get(User, user_id, options=USER_OPTIONS)
        await db_session.delete(user)
        await db_session.commit()
        
async def get_all_users(db_session=None) -> list[User]:
    if db_session == None:
        db_session = session_maker()

    async with db_session:
        query = select(User).options(*USER_OPTIONS)
        data = await db_session.execute(query)
        return data.unique().scalars().all()

# *user traninings 
async def create_user_trainigs(user_id, data: dict, hours, minutes, db_session=None) -> UserTrainings:
    days_data = data["days"]

    if db_session == None:
        db_session = session_maker()
    async with db_session:
        user = await get_user(user_id, db_session)
        if user.trainings:
            return False
        
        new_training = UserTrainings(
            user=user,
            days_data=days_data,
            time_start_hours=hours,
            time_start_minutes=minutes,
            all_body_parts=data["all_body_parts"],
            all_reps_names=data["all_reps_names"],
        )
        db_session.add(new_training)
        await db_session.commit()

        return new_training
    return True

async def get_user_trainings(user_id, db_session=None) -> UserTrainings | None:
    if db_session == None:
        db_session = session_maker()
    async with db_session:
        query = select(UserTrainings).where(UserTrainings.user_id == user_id)
        data = await db_session.execute(query)
        
        try:
            return data.unique().scalars().one()
        
        except NoResultFound:
            return None
        
async def udpate_user_trainings(user_id, data: dict, db_session=None) -> UserTrainings:
    if db_session == None:
        db_session = session_maker()

    async with db_session:
        query = update(UserTrainings).where(UserTrainings.user_id == user_id).values(**data)
        await db_session.execute(query)
        await db_session.commit()

        query = select(UserTrainings).where(UserTrainings.user_id == user_id)
        data = await db_session.execute(query)
        
        return data.unique().scalars().one()
        
async def delete_user_trainings(user_id, db_session=None) -> bool:
    if db_session == None:
        db_session = session_maker()
    async with db_session:
        query = select(User).where(User.id == user_id).options(*USER_OPTIONS)
        data = await db_session.execute(query)
        user = data.unique().scalars().one()

        try:
            await db_session.delete(user.trainings)
            await db_session.commit()
            user.trainings = None

        except NoResultFound:
            user.trainings = None
            return False
        
        return True

# *user finished trainings

# help command for clear text
def get_clear_time(hours, minutes, seconds):

    if len(str(hours)) == 1:
        hours = "0" + str(hours)

    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)

    return f"{hours}:{minutes}.{seconds}"


async def create_user_fihished_trainig(user_id, data: dict, db_session=None) -> UserTrainings:
    # getting training time
    training_time: datetime.timedelta = data["time_end"] - data["time_start"]
    
    training_hours = int(training_time.total_seconds() // 3600)
    training_minutes = int((training_time.total_seconds() % 3600) // 60)
    training_seconds = int(training_time.total_seconds() % 60)
    
    full_training_time = get_clear_time(training_hours, training_minutes, training_seconds)
    
    # aura
    aura_got = 10 / (data["all_reps_count"] - data["reps_finished"] + 1) * (data["all_reps_count"] / 10) # aura based on finished and all reps count. PS maybe I will change it

    if db_session == None:
        db_session = session_maker()
    async with db_session:
        user = await get_user(user_id, db_session)

        # creating object from data
        finished_training = FinishedUserTraining(
            user=user,

            full_training_data=data["full_training_data"],
            # reps
            all_reps_count=data["all_reps_count"],
            reps_finished=data["reps_finished"],
            # time
            time_start=data["time_start"],
            time_end=data["time_end"],
            full_training_time=full_training_time,
            # aura
            aura_got=aura_got,
            # body part
            body_part=data["full_training_data"]["selected_part"]
        )
        # save
        user.finished_trainings.append(finished_training)
        db_session.add(finished_training)

        await db_session.commit()
        return finished_training

# *user stats
async def create_user_stats(user_id, data, db_session=None):
    if db_session == None:
        db_session = session_maker()
    async with db_session:
        user = await get_user(user_id, db_session)

        # creating object from data
        new_stats = UserStats(
            user=user,
            **data
        )
        # save
        user.stats.append(new_stats)
        db_session.add(new_stats)

        await db_session.commit()
        return new_stats