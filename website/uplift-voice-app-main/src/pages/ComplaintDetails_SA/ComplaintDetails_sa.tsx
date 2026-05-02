import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getComplaintById } from "../../services/officer_api_sa";
import jsPDF from "jspdf";
import './ComplaintDetails_sa.css';
import type { GISDetail, OfficerOutput } from "../../components/types_sa/complaint_types_sa";



function LoadingSkeleton() {
  return (
    <div className="page">
      <div className="container_sa">
        <div className="card_sa">
          <div className="card_head_sa">Complaint Details</div>
          <div className="card_body_sa space-y-3">
            <div className="h-6 w-44 bg-gray-200 rounded animate-pulse" />
            <div className="h-4 w-full bg-gray-100 rounded animate-pulse" />
            <div className="h-4 w-5/6 bg-gray-100 rounded animate-pulse" />
            <div className="h-32 w-full bg-gray-100 rounded animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  );
}

function safeText(v: any) {
  if (v === null || v === undefined) return "-";
  return String(v);
}

function addWrappedText(doc: jsPDF, text: string, x: number, y: number, maxWidth: number, lineHeight = 6) {
  const lines = doc.splitTextToSize(text, maxWidth);
  doc.text(lines, x, y);
  return y + lines.length * lineHeight;
}

export default function ComplaintDetails_sa() {
  const { id } = useParams();
  const complaintId = Number(id);

  const [data, setData] = useState<OfficerOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);


  const fileName = useMemo(() => {
    const cat = data?.summary?.category || "complaint";
    return `complaint_${complaintId}_${cat}.pdf`;
  }, [complaintId, data]);

  const load = async () => {
    if (!complaintId || Number.isNaN(complaintId)) {
      setErrorMsg("Invalid complaint id");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setErrorMsg(null);
      const out = await getComplaintById(complaintId);
      const gisAny = out?.gis as any;
      console.log("OFFICER OUT:", out);
      console.log("GIS:", gisAny);
      console.log("poi_details:", gisAny?.poi_details);
      console.log("gis_breakdown:", gisAny?.gis_breakdown);
      setData(out);
    } catch (e: any) {
      setErrorMsg(e?.message || "Failed to load complaint details");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [complaintId]);

  const exportPDF = () => {
    if (!data) return;

    const doc = new jsPDF({ unit: "mm", format: "a4" });
    const marginX = 14;
    const maxWidth = 210 - marginX * 2;
    let y = 14;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    y = addWrappedText(doc, "VOICEUP – OFFICER REPORT", marginX, y, maxWidth, 7);
    y += 2;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);

    // Summary
    doc.setFont("helvetica", "bold");
    y = addWrappedText(doc, "SUMMARY", marginX, y, maxWidth);
    doc.setFont("helvetica", "normal");
    const s = data.summary;
    y = addWrappedText(doc, `Complaint ID: ${safeText(s?.complaint_id)}`, marginX, y + 6, maxWidth);
    y = addWrappedText(doc, `Priority: ${safeText(s?.priority_label)} (Level ${safeText(s?.priority_level)})`, marginX, y, maxWidth);
    y = addWrappedText(doc, `Score: ${safeText(s?.priority_score)} | Risk: ${safeText(s?.risk_category)}`, marginX, y, maxWidth);

    // GIS Analysis Section for PDF
    y += 4;
    if (y > 270) { doc.addPage(); y = 14; }
    doc.setFont("helvetica", "bold");
    y = addWrappedText(doc, "GIS ANALYSIS & STRATEGIC IMPACT", marginX, y, maxWidth);
    doc.setFont("helvetica", "normal");
    y = addWrappedText(doc, `Total GIS Score: ${safeText(data.gis?.gis_score)}`, marginX, y + 6, maxWidth);
    y = addWrappedText(doc, `POI: ${safeText(data.gis?.details_for_popup?.poi_score)} | Road: ${safeText(data.gis?.details_for_popup?.road_score)} | Connectivity: ${safeText(data.gis?.details_for_popup?.connectivity_score)}`, marginX, y, maxWidth);
    y = addWrappedText(doc, `Summary: ${safeText(data.gis?.gis_summary)}`, marginX, y + 2, maxWidth);

    // Landmarks in PDF
    const pois = data.gis?.poi_details || [];
    if (pois.length > 0) {
      y += 2;
      doc.setFont("helvetica", "bold");
      y = addWrappedText(doc, "Impacted Landmarks:", marginX, y, maxWidth);
      doc.setFont("helvetica", "normal");
      y += 4;
      pois.forEach((poi: GISDetail, i: number) => {
        if (y > 270) { doc.addPage(); y = 14; }
        y = addWrappedText(doc, `${i + 1}. ${poi.name} (${poi.type.replace('amenity:', '')}) - ${poi.distance}m`, marginX, y, maxWidth);
      });
    }

    // Complaint Text in PDF
    y += 4;
    doc.setFont("helvetica", "bold");
    y = addWrappedText(doc, "COMPLAINT TEXT", marginX, y, maxWidth);
    doc.setFont("helvetica", "normal");
    y = addWrappedText(doc, safeText(data.complaint?.expanded_text), marginX, y + 6, maxWidth);

    doc.save(fileName);
  };

  if (loading) return <LoadingSkeleton />;
  if (errorMsg || !data) return <div className="p-10 text-red-500">{errorMsg || "No data"}</div>;


  //  Utility to format distance in km/m
  const formatDistanceKm = (kmVal: any) => {
    const km = Number(kmVal);
    if (!Number.isFinite(km) || km <= 0) return "-";
    if (km < 1) return `${Math.round(km * 1000)} m`;
    return `${km.toFixed(2)} km`;
  };

  const altLat = data.gis?.nearest_alt_point_lat;
  const altLon = data.gis?.nearest_alt_point_lon;
  const altPointUrl =
  (typeof altLat === "number" && typeof altLon === "number")
    ? `https://www.google.com/maps?q=${altLat},${altLon}`
    : null;

  const complaintUrl = data.location?.location_link ?? null;

  const getGisMeaning = (category?: string) => {
  const cat = (category || "").toLowerCase();

  const common = {
    poi: "Shows if the complaint is near an important public place.",
    road: "Shows how important the road type is.",
    connectivity: "Shows if people need another way if blocked.",
    crowd: "Shows if this area is usually busy.",
    density: "Shows if similar complaints happened near here before.",
  };

  if (cat === "garbage") {
    return {
      poi: "Shows if garbage is near important public places (school, hospital, market, terminal).",
      road: "Shows if the place is on a main road or small road (truck access).",
      connectivity: "Shows if garbage truck needs a longer way if the road is blocked.",
      crowd: "Shows if this area is usually crowded (garbage affects more people).",
      density: "Shows if the same garbage issue happened near here before.",
    };
  }

  // default = road
  if (cat === "road") {
    return {
      poi: "Shows if this road problem is near important places (school, hospital, terminal, market).",
      road: "Shows how important this road is (main road vs small road).",
      connectivity: "Shows if people need a longer way if this road is blocked.",
      crowd: "Shows if this area is usually busy (traffic/junctions).",
      density: "Shows if similar road complaints happened near here before.",
    };
  }

  return common;

  };
  const meanings = getGisMeaning(data.summary?.category);




return (
  <div className="page">
    <div className="container_sa">
      <div className="flex items-center justify-between mb-4">
        <Link to="/text-complaint" className="text-blue-600 underline">← Back</Link>
        <button className="btn_sa" onClick={exportPDF}>Export PDF</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/*
                          Summary Card 
        */}
        <div className="card_sa">
          <div className="card_head_sa">Final Decision</div>
          <div className="card_body_sa space-y-2">
            <p><b>Priority:</b> {data.summary?.priority_label} (L{data.summary?.priority_level})</p>
            <p><b>Score:</b> {data.summary?.priority_score}</p>
            <p><b>Risk:</b> {data.summary?.risk_category}</p>
          </div>
        </div>

        {/*
                                Location Card 
        */}
        <div className="card_sa">
          <div className="card_head_sa">Location</div>
          <div className="card_body_sa space-y-2">
            <p><b>Place:</b> {data.location?.place_hint ?? "-"}</p>
            <p><b>Lat:</b> {data.location?.latitude}</p>
            <p><b>Lon:</b> {data.location?.longitude}</p>
            <a
              className="text-blue-600 underline"
              href={data.location?.location_link || "#"}
              target="_blank"
              rel="noreferrer"
              >Open Google Map
            </a>
          </div>
        </div>
        
        {/* Complaint Text */}
        <div className="card_sa lg:col-span-2">
          <div className="card_head_sa">Complaint Text</div>
          <div className="card_body_sa leading-relaxed text-gray-700">
            {data.complaint?.expanded_text}
          </div>
        </div>
        {/*
    
                                  GIS DASHBOARD SECTION 
 
        */}
        <div className="card_sa lg:col-span-2">
          <div className="card_head_sa flex justify-between items-center">
            <span>GIS Analysis & Strategic Impact</span>
            <span className="badge_sa bg-blue-100 text-blue-700 font-bold">
              Score: {data.gis?.gis_score ?? 0}
            </span>
          </div>

          <div className="card_body_sa">
            {/* Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
              <div className="metric-box">
                <div className="metric-label">Near Place : {data.gis?.details_for_popup?.poi_score ?? 0}</div>
                <div className="text-xs text-gray-700 mt-1">{meanings.poi}</div>
              </div>

              <div className="metric-box">
                <div className="metric-label">Road Type : {data.gis?.details_for_popup?.road_score ?? 0}</div>
                <div className="text-xs text-gray-700 mt-1">{meanings.road}</div>
              </div>

              <div className="metric-box">
                <div className="metric-label">Detour Need : {data.gis?.details_for_popup?.connectivity_score ?? 0}</div>
                <div className="text-xs text-gray-700 mt-1">{meanings.connectivity}</div>
              </div>

              <div className="metric-box">
                <div className="metric-label">Busy Area : {data.gis?.details_for_popup?.crowd_score ?? 0}</div>
                <div className="text-xs text-gray-700 mt-1">{meanings.crowd}</div>
              </div>

              <div className="metric-box">
                <div className="metric-label">Nearby Complaints Score : {data.gis?.details_for_popup?.complaint_density_score ?? 0}</div>
                <div className="text-xs text-gray-700 mt-1">{meanings.density}</div>
              </div>
            </div>

            {/* Summary */}
            <div className="ai-summary-box mb-6">
              <p className="ai-summary-text">
                <span className="font-semibold">Simple Note:</span>{" "}
                {safeText(data.gis?.gis_summary)?.split("|")?.[0]?.trim()
                  ?.replace("PUBLIC SAFETY RISK:", "Near a school area:")
                  ?.replace("Proximity to", "Near")
                  ?.replace("increases vulnerability for", "more people may be affected, especially")
                  ?.replace("high pedestrian traffic peaks", "students and walkers")
                }
              </p>
            </div>

            {/* Landmarks */}
            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-bold text-gray-700">
                    Nearby Strategic Landmarks (Top 5)
                  </h4>
                  <span className="text-xs text-gray-500">
                    Total detected: {(data.gis?.poi_details || []).length}
                  </span>
                </div>

                {(!data.gis?.poi_details || data.gis.poi_details.length === 0) ? (
                  <div className="text-sm text-gray-500">
                    No strategic landmarks found within the search radius.
                  </div>
                ) : (
                  <div
                    className="bg-gray-50 border rounded-md p-3"
                    style={{ maxHeight: 220, overflowY: "auto" }}
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {(data.gis.poi_details || []).slice(0, 5).map((poi: any, index: number) => {
                        const distance = poi.distance_m ?? poi.distance ?? 0;

                        const typeClean =
                          (poi.type || "")
                            .replace("amenity:", "")
                            .replace("public_transport:", "")
                            .replace("railway:", "")
                            .replace("shop:", "")
                            .replace("landuse:", "");

                        return (
                          <div key={index} className="border rounded-md bg-white p-3 flex flex-col gap-1">
                            <div className="text-sm font-semibold text-gray-800">
                              {poi.name || "Unknown"}
                            </div>

                            <div className="text-xs text-gray-600">
                              <span className="font-medium">Type:</span> {typeClean || "N/A"}
                            </div>

                            <div className="text-xs text-gray-600">
                              <span className="font-medium">Distance:</span> {Math.round(Number(distance))} m 
                                {/* Namma puthusa add panna Distance Type inga varum */}
                                {poi.distance_type && (
                                  <span className="text-gray-400 italic ml-1 text-[10px]">
                                    ({poi.distance_type})
                                  </span>
                                )}                            
                            </div>
                            
                            {/* --- NEW SPATIO-TEMPORAL UI ADDITION --- */}
                            {poi.activity_level_now && (
                              <div className="mt-2 pt-2 border-t border-gray-100 flex flex-col gap-1">
                                <div className="flex items-center gap-2 text-xs">
                                  <span className="font-medium text-gray-600">Activity Now:</span>
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider
                                    ${poi.activity_level_now.toLowerCase() === 'high' 
                                        ? 'bg-red-100 text-red-700' 
                                        : poi.activity_level_now.toLowerCase() === 'medium' 
                                            ? 'bg-orange-100 text-orange-700' 
                                            : 'bg-green-100 text-green-700'}`}
                                  >
                                    {poi.activity_level_now}
                                  </span>
                                </div>
                                {poi.activity_reason && (
                                  <div className="text-[11px] text-gray-500 italic mt-0.5 leading-tight">
                                    ({poi.activity_reason})
                                  </div>
                                )}
                              </div>
                            )}
                            {/* -------------------------------------- */}

                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Connectivity detail line */}
                <div className="mt-3 text-xs text-gray-600 flex flex-wrap items-center gap-2">
                  <span>
                    <span className="font-medium">Alternate routes:</span>{" "}
                    {data.gis?.alternate_routes_count ?? "-"}
                  </span>

                  <span className="text-gray-400">•</span>
                  <span>
                    <span className="font-medium">Nearest alternate route:</span>{" "}
                    {formatDistanceKm(data.gis?.nearest_alt_crossing_km)}
                  </span>

                  {/* Complaint location link */}
                  {complaintUrl ? (
                    <>
                      <span className="text-gray-400">•</span>
                      <a
                        className="text-blue-600 underline"
                        href={complaintUrl}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open complaint location
                      </a>
                    </>
                  ) : null}

                  {/* Alternate route point link (only if backend sends lat/lon) */}
                  {altPointUrl && altPointUrl !== complaintUrl ? (
                    <>
                      <span className="text-gray-400">•</span>
                      <a className="text-blue-600 underline" href={altPointUrl} target="_blank" rel="noreferrer">
                        Open alternate route point
                      </a>
                      {data.gis?.nearest_alt_point_name ? (
                        <span className="text-gray-500">({data.gis.nearest_alt_point_name})</span>
                      ) : null}
                    </>
                  ) : null}
                </div>
              </div>
            </div>
          </div>
{/* 

                                  Recurring part 

*/}
          <div className="card_sa">
            <div className="card_head_sa">Recurring (Repeat Issue)</div>
            <div className="card_body_sa space-y-2">
              <p>
                <b>Nearby complaints (count):</b> {data.recurring?.recurring_count ?? 0}
              </p>
              <p>
                <b>Is recurring:</b> {data.recurring?.is_recurring ? "Yes" : "No"}
              </p>
              <p className="text-sm text-gray-700">
                {safeText(data.recurring?.recurring_reason)}
              </p>
            </div>
          </div>




{/*

                            TRACK CARD 

*/}
          <div className="card_sa">
            <div className="card_head_sa">Track</div>

            <div className="card_body_sa space-y-2">
              <p>
                <b>Current Track:</b>{" "}
                <span className="font-semibold">
                  {data.track?.track ?? "-"}
                </span>
              </p>

              {/* Responsible unit */}
              {data.track?.responsible_unit && (
                <p className="text-sm">
                  <b>Responsible Unit:</b> {data.track.responsible_unit}
                </p>
              )}

              {/* Suggested action */}
              {data.track?.suggested_action && (
                <p className="text-sm">
                  <b>Suggested Action:</b> {data.track.suggested_action}
                </p>
              )}

              {/* Why = Meaning only (professional) */}
              <p className="text-sm text-gray-700">
                <b>Why:</b>{" "}
                {data.track?.track === "Planning"
                  ? "Planning means this complaint may require a longer-term solution such as engineering assessment, resource allocation, or service redesign (beyond routine field work)."
                  : "Operational means this complaint can be handled through routine field operations and maintenance work (day-to-day service delivery)."}
              </p>
            </div>
          </div>

          {/*

                                  Officer Brief Card

*/}
          <div className="card_sa">
            <div className="card_head_sa">Officer Quick Brief</div>

            <div className="card_body_sa space-y-3">
              <div>
                <b>Situation:</b>
                <p className="text-sm text-gray-700 mt-1">
                  {data.officer_brief?.situation ?? "No summary available."}
                </p>
              </div>

              <div>
                <b>Likely impact:</b>
                {Array.isArray(data.officer_brief?.likely_impact) &&
                data.officer_brief!.likely_impact!.length > 0 ? (
                  <ul className="list-disc ml-5 mt-1 text-sm text-gray-700">
                    {data.officer_brief!.likely_impact!.map((x, i) => (
                      <li key={i}>{x}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 mt-1">Not specified.</p>
                )}
              </div>

              <div>
                <b>Handling note:</b>
                <p className="text-sm text-gray-700 mt-1">
                  {data.officer_brief?.handling_note ?? "-"}
                </p>
              </div>

              <div>
                <b>Officer check:</b>
                {Array.isArray(data.officer_brief?.officer_check) &&
                data.officer_brief!.officer_check!.length > 0 ? (
                  <ul className="list-disc ml-5 mt-1 text-sm text-gray-700">
                    {data.officer_brief!.officer_check!.map((x, i) => (
                      <li key={i}>{x}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 mt-1">No checks available.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}