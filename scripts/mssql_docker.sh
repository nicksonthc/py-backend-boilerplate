## DEPLOY ON AWS UBUNTU/ UBUNTU OS 

docker run -e "ACCEPT_EULA=Y" \
   -e "MSSQL_SA_PASSWORD=Pingspace@2025" \
   -e "MSSQL_PID=Developer" \
   -p 1433:1433 \
   --name sqlserver \
   -v mssql-data:/var/opt/mssql \
   -d mcr.microsoft.com/mssql/server:2019-latest
