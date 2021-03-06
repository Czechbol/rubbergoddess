from sqlalchemy import func

from core import utils
from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.karma import Karma, Karma_emoji


class Karma_row_data:
    def __init__(self, value, position):
        self.value = value
        self.position = position


class Karma_data:
    def __init__(self, karma, positive, negative):
        self.karma = karma
        self.positive = positive
        self.negative = negative


class KarmaRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def getMember(self, member_id: int):
        """Return user with given ID"""
        return session.query(Karma).filter(Karma.discord_id == member_id).one_or_none()

    def getMemberCount(self):
        return session.query(Karma).count()

    def updateMemberKarma(self, member_id: int, value: int):
        """Add karma to user"""
        # TODO This is duplicate for `update_karma_get`
        user = self.getMember(member_id)
        if user is None:
            session.add(Karma(discord_id=member_id, karma=value))
        else:
            user.karma += value
        session.commit()

    def getEmotesByValue(self, value):
        emotes = session.query(Karma_emoji).filter(Karma_emoji.value == value)
        return [emote.emoji_ID for emote in emotes]

    # FUNCTIONS BELOW PROBABLY NEED REWRITE
    # TREAT WITH CARE!

    def get_ids_of_emojis_valued(self, val):
        """Returns a list of ids of emojis with specified value"""
        emojis = session.query(Karma_emoji).filter(Karma_emoji.value == val)
        return [emoji.emoji_ID for emoji in emojis]

    def get_all_emojis(self):
        """Returns a list of Karma_emoji objects."""
        return session.query(Karma_emoji)

    def emoji_value(self, emoji_id: str):
        """Returns the value of an emoji.
        If the emoji has not been voted for, returns 0."""
        val = self.emoji_value_raw(emoji_id)
        return val if val is not None else 0

    def emoji_value_raw(self, emoji_id: str):
        """Returns the value of an emoji.
        If the emoji has not been voted for, returns None."""
        emoji = (
            session.query(Karma_emoji)
            .filter(Karma_emoji.emoji_ID == utils.str_emoji_id(emoji_id))
            .one_or_none()
        )
        return emoji.value if emoji else None

    def set_emoji_value(self, emoji_id: str, value: int):
        emoji = Karma_emoji(emoji_ID=utils.str_emoji_id(emoji_id), value=str(value))
        # Merge == 'insert on duplicate key update'
        session.merge(emoji)
        session.commit()

    def remove_emoji(self, emoji_id):
        session.query(Karma_emoji).filter(
            Karma_emoji.emoji_ID == utils.str_emoji_id(emoji_id)
        ).delete()
        session.commit()

    def update_karma(self, member, giver, emoji_value, remove=False):
        self.update_karma_get(member, emoji_value)
        self.update_karma_give(giver, emoji_value, remove)

        session.commit()

    def update_karma_get(self, member, emoji_value):
        members_karma = self.get_karma_object(member.id)
        if members_karma is not None:
            members_karma.karma += emoji_value
        else:
            session.add(Karma(discord_id=member.id, karma=emoji_value))

    def update_karma_give(self, giver, emoji_value, remove):
        if emoji_value > 0:
            if remove:
                column = "negative"
            else:
                column = "positive"
        else:
            if remove:
                column = "positive"
            else:
                column = "negative"

        if column == "negative":
            emoji_value *= -1

        givers_karma = self.get_karma_object(giver.id)
        if givers_karma is not None:
            setattr(givers_karma, column, getattr(givers_karma, column) + emoji_value)
        else:
            new_giver = Karma(discord_id=giver.id)
            setattr(new_giver, column, emoji_value)
            session.add(new_giver)

    def karma_emoji(self, member_id, giver, emoji_id):
        emoji_value = int(self.emoji_value(str(emoji_id)))
        if emoji_value:
            self.update_karma(member_id, giver, emoji_value)

    def karma_emoji_remove(self, member_id, giver, emoji_id):
        emoji_value = int(self.emoji_value(str(emoji_id)))
        if emoji_value:
            self.update_karma(member_id, giver, emoji_value * (-1), True)

    def get_karma_object(self, member_id=None):
        return session.query(Karma).filter(Karma.discord_id == str(member_id)).one_or_none()

    def get_karma_position(self, column, karma):
        value = (
            session.query(func.count(Karma.discord_id)).filter(getattr(Karma, column) > karma).one()
        )
        return value[0] + 1

    def get_karma(self, member_id):
        karma_object = self.get_karma_object(member_id)

        if karma_object is None:
            karma_object = Karma(karma=0, positive=0, negative=0)

        order = self.get_karma_position("karma", karma_object.karma)
        pos_order = self.get_karma_position("positive", karma_object.positive)
        neg_order = self.get_karma_position("negative", karma_object.negative)

        karma = Karma_row_data(karma_object.karma, order)
        positive = Karma_row_data(karma_object.positive, pos_order)
        negative = Karma_row_data(karma_object.negative, neg_order)

        result = Karma_data(karma, positive, negative)
        return result

    def getLeaderboard(self, order: str, offset: int = 0, limit: int = 10):
        return session.query(Karma).order_by(order).offset(offset).limit(limit)

    # Mover module

    def move_user(self, before_id: int, after_id: int) -> int:
        """Replace old user ID with new one.

        Returns
        -------
        `int`: number of altered rows
        """
        user = session.query(Karma).filter(Karma.discord_id == before_id).one_or_none()
        if user is None:
            return 0

        session.query(Karma).filter(Karma.discord_id == after_id).delete()

        user.discord_id = after_id
        session.commit()
        return 1
