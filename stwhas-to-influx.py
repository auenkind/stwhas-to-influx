import argparse
from datetime import datetime, timedelta
import influxdb_client
from stwhas_api_client import StwHasApiClient, StwhasInterval, StwhasUnit, StwHasConsumptionCost
from influxdb_client.client.write_api import SYNCHRONOUS
from pytz import timezone

parser = argparse.ArgumentParser(
                    prog='Stwhas to influx',
                    description='Imports Stwhas power meter usage to influx db')

parser.add_argument('-u', '--user', required=True)
parser.add_argument('-p', '--password', required=True)
parser.add_argument('-m', '--meter-number', required=True)
parser.add_argument('-ih', '--influx-host', required=True)
parser.add_argument('-ip', '--influx-port', default="8086")
parser.add_argument('-it', '--influx-token', required=True)
parser.add_argument('-io', '--influx-organisation', required=True)
parser.add_argument('-ib', '--influx-bucket', required=True)

args = parser.parse_args()

client = influxdb_client.InfluxDBClient(
   url=args.influx_host,
   token=args.influx_token,
   org=args.influx_organisation
)

now = datetime.now()
currentDay = datetime(now.year, now.month, now.day)
#currentDay = currentDay.replace(tzinfo=timezone.utc)

startTime = currentDay - timedelta(days=2)
endTime = currentDay

endTime = endTime + timedelta(hours=4)

apiClient = StwHasApiClient(args.user, args.password)
apiClient.login()

costKwH = apiClient.consumptionCost(startTime, endTime, StwhasInterval.Hour, StwhasUnit.Kwh)
costEur = apiClient.consumptionCost(startTime, endTime, StwhasInterval.Hour, StwhasUnit.Eur)
usage = apiClient.smartMeterData(startTime, endTime, args.meter_number, StwhasInterval.Hour)

#delta = usage.data[0].time.timestamp() - cost.data[0].time.timestamp()

#for i in range(len(usage.data)):
 #   print(usage.data[i].time, usage.data[i].deliverySum, cost.data[i].delivery)

write_api = client.write_api(write_options=SYNCHRONOUS)


def getCost(data:StwHasConsumptionCost):
    ret = []
    for entry in data.data:
        p = influxdb_client.Point("power_usage_info").tag("source", "stwhas")

        if(data.unit == StwhasUnit.Kwh):
            p.field("deliveryForCost", float(entry.delivery))
        else:
            p.field("basePrice", float(entry.baseprice))
            p.field("workPrice", float(entry.workprice))
            p.field("sumPrice", float(entry.sum))
        p.field("interpolatedCost", entry.interpolated)
        p.time(entry.time)
        ret.append(p)
    return ret

points = []
points += getCost(costKwH)
points += getCost(costEur)

for entry in usage.data:
    p = influxdb_client.Point("power_usage_info").tag("source", "stwhas")
    
    for v in [a for a in dir(entry) if not a.startswith('__') and a != 'datetime' and a != 'time' and not callable(getattr(entry, a))]:
        value = float(getattr(entry, v))
        if(v == "interpolated"):
            value = getattr(entry, v)
        p.field(v, value)
    p.time(entry.time)
    points.append(p)

write_api.write(bucket=args.influx_bucket, org=args.influx_organisation, record=points)
number = len(points)
now = datetime.now()
print(f"{now} imported: {number} Data Points")