import { IconTrendingDown, IconTrendingUp } from "@tabler/icons-react"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function SectionCards() {
  return (
    <div className="grid grid-cols-6 md:grid-cols-6 gap-4 px-4 lg:px-6">
      
      {/* === SENSOR 1 (Remaining 3) === */}
      {/* <Card className="@container/card">
        <CardHeader>
          <CardDescription>Sensor 1</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">0.055 kWh</CardTitle>
          <CardAction><Badge variant="outline"><IconTrendingUp /> +12.5%</Badge></CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm"><div className="font-medium">Energy</div></CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Sensor 1</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">49.80 Hz</CardTitle>
          <CardAction><Badge variant="outline"><IconTrendingUp /> +12.5%</Badge></CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm"><div className="font-medium">Frequency</div></CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Sensor 1</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">0.45</CardTitle>
          <CardAction><Badge variant="outline"><IconTrendingUp /> +12.5%</Badge></CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm"><div className="font-medium">Power Factor</div></CardFooter>
      </Card> */}

      <SensorGroup name="Sensor 1" v="228.50 V" a="0.40 A" w="41.90 W" kwh="0.055 kWh" hz="49.80 Hz" pf="0.45" />
      {/* Empty cells to finish Sensor 1's row if needed, but since you are filling all 6, we move to Sensor 2 */}

      {/* === SENSOR 2 === */}
      <SensorGroup name="Sensor 2" v="228.40 V" a="0.16 A" w="37.20 W" kwh="0.091 kWh" hz="49.80 Hz" pf="1.00" />

      {/* === SENSOR 3 === */}
      <SensorGroup name="Sensor 3" v="228.40 V" a="0.09 A" w="1.10 W" kwh="0.040 kWh" hz="49.70 Hz" pf="0.05" />

      {/* === SENSOR 4 === */}
      <SensorGroup name="Sensor 4" v="228.40 V" a="0.09 A" w="2.40 W" kwh="0.002 kWh" hz="49.80 Hz" pf="0.11" />

    </div>
  )
}

/**
 * Quick Helper component to avoid repeating the same 30 lines of code 
 * for every single card.
 */
function SensorGroup({ name, v, a, w, kwh, hz, pf }: any) {
  const metrics = [
    { label: "Voltage", val: v },
    { label: "Current", val: a },
    { label: "Power", val: w },
    { label: "Energy", val: kwh },
    { label: "Frequency", val: hz },
    { label: "PF", val: pf },
  ];

  return (
    <>
      {metrics.map((m) => (
        <Card key={`${name}-${m.label}`} className="@container/card">
          <CardHeader>
            <CardDescription>{name}</CardDescription>
            <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">{m.val}</CardTitle>
            {/* <CardAction>
              <Badge variant="outline"><IconTrendingUp /> +12.5%</Badge>
            </CardAction> */}
          </CardHeader>
          <CardFooter className="flex-col items-start gap-1.5 text-sm">
            <div className="font-medium">{m.label}</div>
          </CardFooter>
        </Card>
      ))}
    </>
  )
}