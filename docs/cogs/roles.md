← Back to [module list](index.md) or [home](../index.md)

# Roles

This module allows users to self-assign some roles via commands or react-to-role mechanics.

## User commands

### subject add (subject) _(subject) (...)_

Add access to the subject's channel. User has to have role allowed to do this (see `faceshifter/subject roles` config entry).

### subject remove (subject) _(subject) (...)_

Remove access to the subject's channel.

### role add (role) _(role) (...)_

Add requested role. If the role is below the bottom limiting role (named **---INTERESTS**), anyone can add it. If the role is above it and below the top limiting role (named **---PROGRAMMES**), user has to have role allowing him to do this (see `faceshifter/programme roles` config entry). If the role is above the top limiting role, access is denied, as they have to be assigned manually.

**programme add (...)** is an alias.

### role remove (role) _(role) (...)_

Remove requested role. Same rules apply as for **role add**.

**programme remove (...)** is an alias.

## Privileged commands

This module has no commands only usable by privileged users.

## Message reactions

If the message starts with a specific string (default is `Role` with newline, see `faceshifter/react-to-role prefix` config entry) or is sent to dedicated channel, it is scanned for emoji-role combination. For every line, reaction is added; when the user clicks on that reaction, they go through the same process as if they have sent **role** or **subject** command.

Example:

```
Role
🤖 bot-development
🖌️ art
🚴 sport
```


← Back to [module list](index.md) or [home](../index.md)
