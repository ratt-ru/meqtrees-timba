#!/usr/bin/env python3
#
#  hot-backup.py: perform a "hot" backup of an Svn repository.
#  Based on the standard script by the same name found in the Debian 
#  subversion-tools package.
#  Incremental backup added by Oleg Smirnov.
#
#  Subversion is a tool for revision control. 
#  See http://subversion.tigris.org for more information.
#    
# ====================================================================
# Copyright (c) 2000-2004 CollabNet.  All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.  The terms
# are also available at http://subversion.tigris.org/license-1.html.
# If newer versions of this license are posted there, you may use a
# newer version instead, at your option.
#
# This software consists of voluntary contributions made by many
# individuals.  For exact contribution history, see the revision
# history and logs, available at http://subversion.tigris.org/.
# ====================================================================

######################################################################

import sys, os, shutil, string, re

######################################################################
# Global Settings

# Path to svnlook utility
svnlook = "/usr/bin/svnlook"

# Path to svnadmin utility
svnadmin = "/usr/bin/svnadmin"

# Number of backups to keep around (0 for "keep them all")
num_backups = 8

tar_exec = "/bin/tar"
scp_exec = "/usr/bin/scp"
gzip = "/bin/gzip";

# Path to redundant backup locations
backup_locations = [ 
  '/net/lofar10/home/backups/svn',
  '/net/birch/home/backups/svn',
  '/net/cedar/home/backups/svn'
];

# name of status file
status_file = ".last_backup";


######################################################################
# Command line arguments

# if called as incr-*, perform incremental backup
incremental = os.path.basename(sys.argv[0]).startswith("incr-");

if len(sys.argv) != 3:
  print(("Usage: ", os.path.basename(sys.argv[0]), " <repos_path> <backup_path>"))
  sys.exit(1)

# Path to repository
repo_dir = sys.argv[1]
repo = os.path.basename(os.path.abspath(repo_dir))

# Where to store the repository backup.  The backup will be placed in
# a *subdirectory* of this location, named after the youngest
# revision.
backup_dir = sys.argv[2]
status_file = os.path.join(backup_dir,status_file);

######################################################################
# Helper functions

def comparator(a, b):
  # We pass in filenames so there is never a case where they are equal.
  regexp = re.compile("-(?P<revision>[0-9]+)(-(?P<increment>[0-9]+))?$")
  matcha = regexp.search(a)
  matchb = regexp.search(b)
  reva = int(matcha.groupdict()['revision'])
  revb = int(matchb.groupdict()['revision'])
  if (reva < revb):
    return -1
  elif (reva > revb):
    return 1
  else:
    inca = matcha.groupdict()['increment']
    incb = matchb.groupdict()['increment']
    if not inca:
      return -1
    elif not incb:
      return 1;
    elif (int(inca) < int(incb)):
      return -1
    else:
      return 1

######################################################################
# Main

if incremental:
  print(("Beginning incremental backup of '"+ repo_dir + "'."))
else:
  print(("Beginning full backup of '"+ repo_dir + "'."))


### Step 1: get the youngest revision.

infile, outfile, errfile = os.popen3(svnlook + " youngest " + repo_dir)
stdout_lines = outfile.readlines()
stderr_lines = errfile.readlines()
outfile.close()
infile.close()
errfile.close()

youngest = string.strip(stdout_lines[0])
print(("Youngest revision is", youngest))

if not incremental:
  ###########################################
  ### FULL BACKUP 			  ###
  ###########################################
  
  ### Step 2: Find next available backup path

  backup_subdir = os.path.join(backup_dir, repo + "-" + youngest)

  # If there is already a backup of this revision, then append the
  # next highest increment to the path. We still need to do a backup
  # because the repository might have changed despite no new revision
  # having been created. We find the highest increment and add one
  # rather than start from 1 and increment because the starting
  # increments may have already been removed due to num_backups.

  regexp = re.compile("^" + repo + "-" + youngest + "(-(?P<increment>[0-9]+))?$")
  directory_list = os.listdir(backup_dir)
  young_list = [x for x in directory_list if regexp.search(x)]
  from past.builtins import cmp
  from functools import cmp_to_key
  if young_list:
    young_list.sort(key=cmp_to_key(comparator))
    increment = regexp.search(young_list.pop()).groupdict()['increment']
    if increment:
      backup_subdir = os.path.join(backup_dir, repo + "-" + youngest + "-"
                                   + str(int(increment) + 1))
    else:
      backup_subdir = os.path.join(backup_dir, repo + "-" + youngest + "-1")

  ### Step 3: Ask subversion to make a hot copy of a repository.
  ###         copied last.

  print(("Backing up repository to " + backup_subdir));
  err_code = os.spawnl(os.P_WAIT, svnadmin, "svnadmin", "hotcopy", repo_dir, 
                       backup_subdir, "--clean-logs")
  if(err_code != 0):
    print("Unable to backup the repository.")
    sys.exit(err_code)
  else:
    print("Done.")

  ### Step 4. Compress the backup into a tarball and send over to other places
  print("Making tarball of backup");
  tarball = backup_subdir + ".tgz";
  err_code = os.system("cd "+backup_dir+"; tar zcf "+tarball+" "+os.path.basename(backup_subdir));
  if(err_code != 0):
    print(("Unable to create "+tarball));
    sys.exit(err_code)
  else:
    print("Done.")

  ### Step 5. Copy tarball to backup locations
  for dest in backup_locations:
    err_code = os.spawnl(os.P_WAIT,scp_exec,"scp",tarball,dest);
    if(err_code != 0):
      print(("Unable to copy "+tarball+" to "+dest));

  ### Step 6. Remove tarball
  print(("Removing "+tarball));
  os.remove(tarball);

  ### Step 7. Write out status file for incremental backups
  open(status_file,'w').write(youngest+" "+backup_subdir);

  ### Step 8. finally, remove all repository backups other than the last
  ###         NUM_BACKUPS.

  if num_backups > 0:
    regexp = re.compile("^" + repo + "-[0-9]+(-[0-9]+)?$")
    directory_list = os.listdir(backup_dir)
    old_list = [x for x in directory_list if regexp.search(x)]
    old_list.sort(comparator)
    del old_list[max(0,len(old_list)-num_backups):]
    for item in old_list:
      old_backup_subdir = os.path.join(backup_dir, item)
      print(("Removing old backup: " + old_backup_subdir))
      shutil.rmtree(old_backup_subdir)
else:
  ###########################################
  ### INCREMENTAL BACKUP		  ###
  ###########################################
  
  ### Get previous backup info from status file
  backup_rev,backup_subdir = \
    open(status_file).readline().split(" ");
  rev0 = int(backup_rev);
  rev1 = int(youngest);
  if not os.path.isdir(backup_subdir):
    print(("Can't find full backup in "+backup_subdir));
    sys.exit(1);
    
  ### Check if incremental backup is needed
  if rev0 == rev1:
    print(("Already backed up to revision "+str(rev1)));
    sys.exit(0);
  revs = "%d:%d"%(rev0+1,rev1);
  incr_backup_file = os.path.join(backup_subdir,"incr:"+revs+".gz");
  
  ### Do the backup
  print(("Writing incremental backup for revisions "+revs));
  err_code = os.system(svnadmin+" dump "+repo_dir+" --revision "+
    revs+" --incremental |"+gzip+" >"+incr_backup_file);
  if(err_code != 0):
    print(("Incremental backup to "+incr_backup_file+" failed"));
    sys.exit(err_code)
  else:
    print("Done.")
    
  ### Write out status file for incremental backups
  open(status_file,'w').write(youngest+" "+backup_subdir);
  
  ### Copy to redundant places
  for dest in backup_locations:
    err_code = os.spawnl(os.P_WAIT,scp_exec,"scp",incr_backup_file,dest);
    if(err_code != 0):
      print(("Unable to copy "+incr_backup_file+" to "+dest));
