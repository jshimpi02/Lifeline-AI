import "dotenv/config";

const LIFELINE_API =
  process.env.LIFELINE_API || "http://127.0.0.1:8000";

const SF_LAT = 37.7749;
const SF_LNG = -122.4194;

async function sendToLifeline(report: string) {
  const res = await fetch(`${LIFELINE_API}/agent/asi-process-report`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      raw_text: report,
      source: "weather",
    }),
  });

  const data = await res.json();
  console.log("✓ Sent weather report:", report);
  return data;
}

async function fetchWeatherData() {
  const url =
    `https://api.open-meteo.com/v1/forecast` +
    `?latitude=${SF_LAT}` +
    `&longitude=${SF_LNG}` +
    `&current=temperature_2m,precipitation,rain,wind_speed_10m` +
    `&hourly=precipitation_probability,precipitation,rain,wind_speed_10m` +
    `&forecast_days=1`;

  const res = await fetch(url);
  return res.json();
}

function generateWeatherReports(data: any): string[] {
  const reports: string[] = [];

  const current = data.current;
  const hourly = data.hourly;

  const temp = current.temperature_2m;
  const rain = current.rain || 0;
  const precipitation = current.precipitation || 0;
  const wind = current.wind_speed_10m || 0;

  const maxRain = Math.max(...(hourly.rain || [0]));
  const maxPrecipProb = Math.max(
    ...(hourly.precipitation_probability || [0])
  );
  const maxWind = Math.max(...(hourly.wind_speed_10m || [0]));

  reports.push(
    `Weather update for San Francisco: current temperature is ${temp}°C, wind speed is ${wind} km/h, rainfall is ${rain} mm.`
  );

  if (rain > 0 || precipitation > 0 || maxRain > 0.5) {
    reports.push(
      `Weather agent reports rainfall in San Francisco with possible flood risk near low-lying roads and intersections.`
    );
  }

  if (maxPrecipProb >= 50) {
    reports.push(
      `Weather agent reports ${maxPrecipProb}% precipitation probability today in San Francisco. Emergency teams should monitor flood-prone areas.`
    );
  }

  if (wind >= 25 || maxWind >= 30) {
    reports.push(
      `Weather agent reports strong winds in San Francisco. Potential risk for downed branches, traffic disruption, and power outages.`
    );
  }

  return reports;
}

async function runWeatherFeed() {
  console.log("Starting Weather Intelligence Agent...");

  const weather = await fetchWeatherData();
  const reports = generateWeatherReports(weather);

  for (const report of reports) {
    await sendToLifeline(report);
  }

  console.log("Weather feed complete.");
}

runWeatherFeed().catch(console.error);