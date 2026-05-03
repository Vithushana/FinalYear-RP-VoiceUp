import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import type { ComplaintListItem } from "../types_sa/complaint_types_sa";
import "leaflet/dist/leaflet.css";

// If markers are invisible, you may need leaflet marker icon fix.
// (Skip for now if your markers already show.)

type Props = {
  complaints: ComplaintListItem[];
  selectedId: number | null;
  onSelect: (id: number) => void; // marker click -> dashboard select
};

function FitBounds_sa({ complaints }: { complaints: ComplaintListItem[] }) {
  const map = useMap();

  const points = useMemo(() => {
    return complaints
      .filter((c) => typeof c.latitude === "number" && typeof c.longitude === "number")
      .map((c) => [c.latitude as number, c.longitude as number] as [number, number]);
  }, [complaints]);

  useEffect(() => {
    if (!points.length) return;

    if (points.length === 1) {
      map.setView(points[0], 14);
      return;
    }

    // fit bounds
    // @ts-ignore (leaflet types ok in runtime)
    map.fitBounds(points, { padding: [40, 40] });
  }, [map, points]);

  return null;
}

function FocusSelected_sa({
  complaints,
  selectedId,
}: {
  complaints: ComplaintListItem[];
  selectedId: number | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (!selectedId) return;
    const c = complaints.find((x) => x.id === selectedId);
    if (!c) return;
    if (typeof c.latitude !== "number" || typeof c.longitude !== "number") return;

    map.setView([c.latitude, c.longitude], 15);
  }, [map, complaints, selectedId]);

  return null;
}

export default function SLMap_sa({ complaints, selectedId, onSelect }: Props) {
  const center: [number, number] = [7.8731, 80.7718]; // Sri Lanka center

  const valid = complaints.filter(
    (c) => typeof c.latitude === "number" && typeof c.longitude === "number"
  );

  return (
    <div className="h-[420px] w-full rounded-xl overflow-hidden border border-gray-200">
      <MapContainer center={center} zoom={7} className="h-full w-full">
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* auto fit when filter changes */}
        <FitBounds_sa complaints={valid} />

        {/* focus when list selected */}
        <FocusSelected_sa complaints={valid} selectedId={selectedId} />

        {valid.map((c) => (
          <Marker
            key={c.id}
            position={[c.latitude as number, c.longitude as number]}
            eventHandlers={{
              click: () => onSelect(c.id), // marker click -> highlight list + navigate (we do in dashboard)
            }}
          >
            <Popup>
              <div className="space-y-1">
                <div className="font-semibold">
                  #{c.id} • {c.category}
                </div>
                <div className="text-sm">
                  {(c.text_expanded || "").slice(0, 80)}
                  {(c.text_expanded || "").length > 80 ? "..." : ""}
                </div>
                <div className="text-xs text-gray-600">
                  {c.priority_level ? `Priority: P${c.priority_level}` : "No priority"}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
