import os
import pwd
import grp
import logging

logger = logging.getLogger(__name__)

def drop_privileges(username: str = "nobody", group: str = "nogroup") -> bool:
    """
    Drop privileges from root to the specified user and group.
    Only takes effect if run as root (UID == 0).
    If SUDO_USER is present in environment, drops privileges to that user/group.
    """
    if os.getuid() != 0:
        logger.debug("Not running as root, no privileges to drop.")
        return False

    try:
        # 1. Identify target GID
        target_gid = None
        # Attempt to get GID for specified group name
        try:
            target_gid = grp.getgrnam(group).gr_gid
        except KeyError:
            # Fallbacks for different Unix distributions
            for gname in ["nobody", "nogroup", "daemon"]:
                try:
                    target_gid = grp.getgrnam(gname).gr_gid
                    group = gname
                    break
                except KeyError:
                    continue
            if target_gid is None:
                target_gid = 65534  # Fallback to standard nobody GID

        # 2. Identify target UID
        target_uid = None
        try:
            target_uid = pwd.getpwnam(username).pw_uid
        except KeyError:
            for uname in ["nobody", "daemon"]:
                try:
                    target_uid = pwd.getpwnam(uname).pw_uid
                    username = uname
                    break
                except KeyError:
                    continue
            if target_uid is None:
                target_uid = 65534  # Fallback to standard nobody UID

        # 3. Detect sudo environment to drop to original user
        sudo_user = os.environ.get("SUDO_USER")
        if sudo_user:
            try:
                pw = pwd.getpwnam(sudo_user)
                target_uid = pw.pw_uid
                target_gid = pw.pw_gid
                username = sudo_user
                group = grp.getgrgid(target_gid).gr_name
            except KeyError:
                logger.warning(f"Could not resolve SUDO_USER '{sudo_user}' to drop privileges.")

        # 4. Perform the transition
        os.setgroups([])  # Remove all supplementary groups
        os.setgid(target_gid)
        os.setuid(target_uid)

        logger.info(f"Dropped privileges to user '{username}' (UID: {target_uid}), group '{group}' (GID: {target_gid})")
        return True
    except Exception as e:
        logger.error(f"Failed to drop privileges: {e}")
        return False
