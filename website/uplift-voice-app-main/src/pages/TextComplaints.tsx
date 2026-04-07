import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAllComplaints } from "../services/officer_api_sa";

import SLMap_sa from "../components/SLMap_sa/SLMap_sa";
import type { ComplaintListItem } from "../components/types_sa/complaint_types_sa";
import "leaflet/dist/leaflet.css";
import Sidebar from '@/components/layout/Sidebar';

type SortMode = "newest" | "oldest";

export default function TextComplaints() {
  const navigate = useNavigate();

  const [items, setItems] = useState<ComplaintListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // controls
  const [q, setQ] = useState("");
  const [category, setCategory] = useState<"all" | "road" | "garbage">("all");
  const [sort, setSort] = useState<SortMode>("newest");
  const [pageSize, setPageSize] = useState<number>(5);

  // pagination
  const [page, setPage] = useState(1);

  // selected complaint (for map focus highlight)
  const [selectedId, setSelectedId] = useState<number | null>(null);
  // month filter: 'all' or label like 'Mar 2026'
  const [monthFilter, setMonthFilter] = useState<'all' | string>('all');

  // ONE place to load data (with retry)
  async function loadData() {
    try {
      setLoading(true);
      setErrorMsg(null);
      const data = await getAllComplaints();
      setItems(data || []);
    } catch (e: any) {
      setErrorMsg(
        e?.message || "Failed to load complaints. Check backend and try again."
      );
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Initial load + periodic polling and focus-refresh so UI reflects external DB changes
    loadData();

    const intervalId = setInterval(() => {
      loadData();
    }, 30000); // every 30 seconds

    const onFocus = () => loadData();
    window.addEventListener("focus", onFocus);

    return () => {
      clearInterval(intervalId);
      window.removeEventListener("focus", onFocus);
    };
  }, []);


  // filter + sort (rename fixed: don't use "ComplaintListItem" as variable name)
  const filteredSorted = useMemo(() => {
    let list = [...items];

    // month filter (if applied)
    if (monthFilter !== 'all') {
      const [monShort, yearStr] = monthFilter.split(' ');
      const yearNum = Number(yearStr);
      // convert short month name to index
      const monthIndex = new Date(Date.parse(monShort + " 1, 2000")).getMonth();
      list = list.filter((c) => {
        if (!c.created_at) return false;
        const d = new Date(c.created_at);
        return d.getMonth() === monthIndex && d.getFullYear() === yearNum;
      });
    }

    // category filter
    if (category !== "all") {
      list = list.filter((c) => c.category === category);
    }

    // search filter
    const query = q.trim().toLowerCase();
    if (query) {
      list = list.filter((c) => {
        const text = (c.text_expanded || "").toLowerCase();
        return (
          text.includes(query) ||
          (c.category || "").toLowerCase().includes(query)
        );
      });
    }

    // sort
    list.sort((a, b) => {
      const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
      const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
      return sort === "newest" ? bTime - aTime : aTime - bTime;
    });

    return list;
  }, [items, q, category, sort, monthFilter]);

  // compute months from the full items list (unfiltered) for month selection UI
  const monthsFromItems = useMemo(() => {
    const now = new Date();
    const months: Array<{ label: string; count: number }> = [];
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthNum = d.getMonth();
      const yearNum = d.getFullYear();
      const label = d.toLocaleString(undefined, { month: "short" }) + " " + yearNum;
      const count = items.filter((c) => {
        if (!c.created_at) return false;
        const cd = new Date(c.created_at);
        return cd.getMonth() === monthNum && cd.getFullYear() === yearNum;
      }).length;
      months.push({ label, count });
    }
    return months;
  }, [items]);

  // stats (based on filtered list)
  const stats = useMemo(() => {
    const total = filteredSorted.length;
    // NOTE: only if backend returns priority_level in list API
    const high = filteredSorted.filter((c: any) => c.priority_level === 1).length;
    const medium = filteredSorted.filter((c: any) => c.priority_level === 2).length;
    const low = filteredSorted.filter((c: any) => c.priority_level === 3).length;
    return { total, high, medium, low };
  }, [filteredSorted]);

  // pagination calc
  const total = filteredSorted.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(page, totalPages);

  const paged = useMemo(() => {
    const start = (safePage - 1) * pageSize;
    return filteredSorted.slice(start, start + pageSize);
  }, [filteredSorted, safePage, pageSize]);

  // page reset when filters change
  useEffect(() => {
    setPage(1);
  }, [q, category, sort, pageSize]);

  const clearFilters = () => {
    setQ("");
    setCategory("all");
    setSort("newest");
    setPageSize(5);
    setSelectedId(null);
  };

  // Loading skeleton (basic) – uses your same card styles
  const LoadingSkeleton = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="card_sa">
        <div className="card_head_sa">Sri Lanka Live Map (Filtered)</div>
        <div className="card_body_sa">
          <div className="h-64 bg-gray-100 rounded-lg animate-pulse" />
        </div>
      </div>

      <div className="card_sa">
        <div className="card_head_sa flex items-center justify-between">
          <span>Complaints List</span>
          <span className="text-sm text-gray-600">Loading...</span>
        </div>

        <div className="card_body_sa space-y-3">
          {[1, 2, 3, 4, 5].map((n) => (
            <div key={n} className="p-3 border border-gray-200 rounded-lg">
              <div className="h-4 w-40 bg-gray-200 rounded mb-2 animate-pulse" />
              <div className="h-3 w-full bg-gray-100 rounded mb-1 animate-pulse" />
              <div className="h-3 w-5/6 bg-gray-100 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  //Error card with Retry button – uses your card style
  const ErrorCard = ({ message }: { message: string }) => (
    <div className="card_sa mb-4">
      <div className="card_head_sa flex items-center justify-between">
        <span>Error</span>
        <button className="btn_sa" onClick={loadData}>
          Retry
        </button>
      </div>
      <div className="card_body_sa">
        <p className="text-red-600 font-semibold mb-1">Something went wrong</p>
        <p className="text-sm text-gray-700">{message}</p>

        <p className="text-xs text-gray-500 mt-3">
          Tip: Check backend running at <b>http://127.0.0.1:8000</b>
        </p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      <div className="flex-1">
        <div className="container_sa">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Citizen Text Complaint</h1>

          {/* Refresh now uses loadData (not reload) */}
          <button className="btn_sa" onClick={loadData} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
          <div className="card_sa">
            <div className="card_body_sa">
              <p className="text-xs text-gray-500">Total</p>
              <p className="text-2xl font-bold">{stats.total}</p>
            </div>
          </div>

          <div className="card_sa">
            <div className="card_body_sa flex flex-col items-center justify-center">
              <p className="text-xs text-gray-500 text-center">List 12 months</p>
              <div className="mt-2">
                <select
                  className="input_sa w-40"
                  value={monthFilter}
                  onChange={(e) => setMonthFilter(e.target.value)}
                >
                  <option value="all">All months ({items.length})</option>
                  {monthsFromItems.map((m) => (
                    <option key={m.label} value={m.label}>
                      {m.label} ({m.count})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="card_sa">
            <div className="card_body_sa">
              <p className="text-xs text-gray-500">High</p>
              <p className="text-2xl font-bold">{stats.high}</p>
            </div>
          </div>

          <div className="card_sa">
            <div className="card_body_sa">
              <p className="text-xs text-gray-500">Medium</p>
              <p className="text-2xl font-bold">{stats.medium}</p>
            </div>
          </div>

          <div className="card_sa">
            <div className="card_body_sa">
              <p className="text-xs text-gray-500">Low</p>
              <p className="text-2xl font-bold">{stats.low}</p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="card_sa mb-4">
          <div className="card_head_sa flex items-center justify-between">
            <span>Search / Filter / Sort</span>
            <button className="btn_sa" onClick={clearFilters} disabled={loading}>
              Clear Filters
            </button>
          </div>

          <div className="card_body_sa grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              className="input_sa"
              placeholder="Search complaint text or category..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              disabled={loading}
            />

            <select
              className="input_sa"
              value={category}
              onChange={(e) => setCategory(e.target.value as any)}
              disabled={loading}
            >
              <option value="all">All Categories</option>
              <option value="road">Road</option>
              <option value="garbage">Garbage</option>
            </select>

            <select
              className="input_sa"
              value={sort}
              onChange={(e) => setSort(e.target.value as SortMode)}
              disabled={loading}
            >
              <option value="newest">Sort: Newest First</option>
              <option value="oldest">Sort: Oldest First</option>
            </select>

            <select
              className="input_sa"
              value={pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
              disabled={loading}
            >
              <option value={5}>Page size: 5</option>
              <option value={10}>Page size: 10</option>
              <option value={20}>Page size: 20</option>
              <option value={50}>Page size: 50</option>
            </select>
          </div>
        </div>

        {/* Error UI with Retry */}
        {errorMsg ? <ErrorCard message={errorMsg} /> : null}

        {/* Loading skeleton */}
        {loading ? (
          <LoadingSkeleton />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="card_sa">
              <div className="card_head_sa">
                Sri Lanka Live Map (Filtered)
                {selectedId ? (
                  <span className="text-sm text-gray-600 ml-2">
                    • Selected: #{selectedId}
                  </span>
                ) : null}
              </div>

              <div className="card_body_sa" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
                <SLMap_sa
                  complaints={filteredSorted}
                  selectedId={selectedId}
                  onSelect={(id: number) => {
                    setSelectedId(id);
                    navigate(`/complaint/${id}`);
                  }}
                />
              </div>
            </div>

            <div className="card_sa">
              <div className="card_head_sa flex items-center justify-between">
                <span>Complaints List</span>
                <span className="text-sm text-gray-600">
                  Showing {paged.length} / {total}
                </span>
              </div>

              <div className="card_body_sa">
                {total === 0 ? (
                  <p>No complaints found.</p>
                ) : (
                  <>
                    <div className="space-y-3">
                      {paged.map((c: any) => {
                        const isSelected = selectedId === c.id;
                        const pLevel = c.priority_level as number | undefined;

                        return (
                          <div
                            key={c.id}
                            className={
                              "p-3 border rounded-lg cursor-pointer " +
                              (isSelected
                                ? "border-blue-400 bg-blue-50"
                                : "border-gray-200 hover:bg-gray-50")
                            }
                            onClick={() => {
                              setSelectedId(c.id);
                              setTimeout(() => {
                                navigate(`/complaint/${c.id}`);
                              }, 150);
                            }}
                            role="button"
                            tabIndex={0}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                setSelectedId(c.id);
                                navigate(`/complaint/${c.id}`);
                              }
                            }}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-semibold">
                                #{c.id} • {c.category}
                              </span>

                              {pLevel ? (
                                <span className="badge_sa bg-gray-100 text-gray-700">
                                  P{pLevel}
                                </span>
                              ) : (
                                <span className="badge_sa bg-gray-100 text-gray-500">
                                  No Priority
                                </span>
                              )}
                            </div>

                            <p className="text-sm text-gray-700 mt-1 line-clamp-2">
                              {c.text_expanded}
                            </p>

                            {c.created_at ? (
                              <p className="text-xs text-gray-500 mt-1">
                                {new Date(c.created_at).toLocaleString()}
                              </p>
                            ) : null}
                          </div>
                        );
                      })}
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between mt-4">
                      <button
                        className="btn_sa disabled:opacity-40"
                        disabled={safePage <= 1}
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                      >
                        Prev
                      </button>

                      <p className="text-sm text-gray-700">
                        Page <b>{safePage}</b> / {totalPages}
                      </p>

                      <button
                        className="btn_sa disabled:opacity-40"
                        disabled={safePage >= totalPages}
                        onClick={() =>
                          setPage((p) => Math.min(totalPages, p + 1))
                        }
                      >
                        Next
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
