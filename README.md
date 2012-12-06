lsci_2012
=========

Using amazon aws and starcluster for evolutionary algorithm.

Requirements:
- starcluster (easy_install starcluster)
- AWS Credentials

Configuration:
- Set up a star cluster configuration file with your AWS credentials and the number of nodes etc
- You can use the default starcluster aws image
- Copy the starcluster/conf.dist to starcluster/conf and fill in your credentials and generate the rsa key
- If you change the file structure and logins please be aware of the following points:
1. The script needs an NFS mounted /home folder on all nodes
2. SSH login has to be without password (default starcluster vm)
3. The /root folder is used to process files local, so don't share it on NFS

Commands:
./start.sh path/to/config clustername
./terminate.sh path/to/config clustername