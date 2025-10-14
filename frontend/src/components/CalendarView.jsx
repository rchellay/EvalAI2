import React, { useState, useEffect } from "react";
import { Calendar, momentLocalizer } from "react-big-calendar";
import { useNavigate } from "react-router-dom";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";
import "../calendar-custom.css";
import api from "../lib/axios";
import { toast } from "react-hot-toast";
import { RRule } from "rrule";
import "moment/locale/es";

// Configurar español como idioma predeterminado con lunes como primer día
moment.updateLocale("es", {
  week: {
    dow: 1, // Lunes como primer día (0 = domingo, 1 = lunes)
    doy: 4  // Usado para determinar la primera semana del año
  }
});
moment.locale("es");
const localizer = momentLocalizer(moment);

export default function CalendarView() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [subjects, setSubjects] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedDayEvents, setSelectedDayEvents] = useState([]);

  useEffect(() => {
    const loadSubjects = async () => {
      try {
        const res = await api.get("/subjects/");
        const subjectsData = Array.isArray(res.data) ? res.data : res.data.results || [];
        setSubjects(subjectsData);
        
        // Cargar eventos iniciales para el mes actual
        if (subjectsData.length > 0) {
          loadEventsForCurrentMonth(subjectsData);
        }
      } catch (err) {
        console.error("Error:", err);
        toast.error("Error al cargar asignaturas");
      }
    };
    loadSubjects();
  }, []);

  const loadEventsForCurrentMonth = (subjectsData) => {
    // Primer día visible: lunes de la semana que contiene el primer día del mes
    let firstDay = moment().startOf('month').isoWeekday(1);
    if (firstDay.month() < moment().month()) {
      firstDay = moment().startOf('month');
    }
    // Último día visible: domingo de la semana que contiene el último día del mes
    let lastDay = moment().endOf('month').isoWeekday(7);
    if (lastDay.month() > moment().month()) {
      lastDay = moment().endOf('month');
    }
    const range = {
      start: firstDay.toDate(),
      end: lastDay.toDate()
    };
    generateEvents(subjectsData, range);
  };

  const generateEvents = (subjectsData, range) => {
    setLoading(true);
    try {
      let startDate, endDate;
      if (Array.isArray(range)) {
        startDate = moment(range[0]).format("YYYY-MM-DD");
        endDate = moment(range[range.length - 1]).format("YYYY-MM-DD");
      } else {
        startDate = moment(range.start).format("YYYY-MM-DD");
        endDate = moment(range.end).format("YYYY-MM-DD");
      }

      console.log('Generating events from', startDate, 'to', endDate);

      const subjectEvents = [];
      
      // Mapeo correcto de días: el backend guarda en inglés minúsculas
      // Usar los objetos RRule.MO, RRule.TU, etc. para byweekday
      const dayMap = {
        'monday': RRule.MO,
        'tuesday': RRule.TU,
        'wednesday': RRule.WE,
        'thursday': RRule.TH,
        'friday': RRule.FR,
        'saturday': RRule.SA,
        'sunday': RRule.SU
      };
      
      for (const subject of subjectsData) {
        if (subject.days && Array.isArray(subject.days) && subject.days.length > 0) {
          console.log(`Processing subject: ${subject.name}, days:`, subject.days);
          
          const weekdays = subject.days
            .map(day => dayMap[day.toLowerCase()])
            .filter(Boolean);
          
          console.log(`Mapped weekdays for ${subject.name}:`, weekdays);
          
          if (weekdays.length > 0) {
            const rule = new RRule({
              freq: RRule.WEEKLY,
              byweekday: weekdays,
              dtstart: moment(startDate).toDate(),
              until: moment(endDate).toDate()
            });
            
            const dates = rule.all();
            console.log(`Generated ${dates.length} dates for ${subject.name}:`);
            dates.slice(0, 10).forEach((d, i) => {
              const jsDate = new Date(d);
              console.log(`  [${i}] ${moment(d).format('YYYY-MM-DD dddd')} | jsDate.getDay(): ${jsDate.getDay()}`);
            });

            dates.forEach((date) => {
              const [startHour, startMin] = (subject.start_time || "09:00:00").split(":");
              const [endHour, endMin] = (subject.end_time || "10:00:00").split(":");
              subjectEvents.push({
                id: `subject-${subject.id}-${date.toISOString()}`,
                title: subject.name,
                start: moment(date).utc().hour(parseInt(startHour)).minute(parseInt(startMin)).toDate(),
                end: moment(date).utc().hour(parseInt(endHour)).minute(parseInt(endMin)).toDate(),
                allDay: false,
                resource: { 
                  type: "subject", 
                  color: subject.color || "#3B82F6",
                  subjectId: subject.id
                },
              });
            });
          }
        }
      }

      console.log('Total events generated:', subjectEvents.length);
      setEvents(subjectEvents);
    } catch (err) {
      console.error("Error generating events:", err);
      toast.error("Error al cargar eventos");
    } finally {
      setLoading(false);
    }
  };

  const handleRangeChange = async (range) => {
    generateEvents(subjects, range);
  };

  const handleSelectSlot = (slotInfo) => {
    setSelectedDate(slotInfo.start);
    const dayEvents = events.filter(event => 
      moment(event.start).format("YYYY-MM-DD") === moment(slotInfo.start).format("YYYY-MM-DD")
    );
    setSelectedDayEvents(dayEvents);
  };

  const handleNavigate = (date) => {
    setSelectedDate(date);
    const dayEvents = events.filter(event => 
      moment(event.start).format("YYYY-MM-DD") === moment(date).format("YYYY-MM-DD")
    );
    setSelectedDayEvents(dayEvents);
  };

  useEffect(() => {
    const dayEvents = events.filter(event => 
      moment(event.start).format("YYYY-MM-DD") === moment(selectedDate).format("YYYY-MM-DD")
    );
    setSelectedDayEvents(dayEvents);
  }, [events, selectedDate]);

  const eventStyleGetter = (event) => ({
    style: {
      backgroundColor: event.resource?.color || "#3B82F6",
      borderRadius: "4px", opacity: 0.8, color: "white", border: "0px", display: "block",
    },
  });

  const messages = {
    allDay: "Todo el día", previous: "Anterior", next: "Siguiente", today: "Hoy",
    month: "Mes", week: "Semana", day: "Día", agenda: "Agenda", date: "Fecha",
    time: "Hora", event: "Evento",
    noEventsInRange: "No hay eventos", showMore: (total) => `+ Ver más (${total})`,
  };

  // Formatos personalizados para español
  const formats = {
    weekdayFormat: (date, culture, localizer) => localizer.format(date, 'dddd', culture).toUpperCase().substring(0, 3),
  };  return (
    <div className="h-full flex bg-gray-50">
      <div className="w-64 bg-white border-r border-gray-200 p-2 overflow-y-auto calendar-sidebar">
        <h2 className="text-lg font-bold text-gray-800 mb-2">
          {moment(selectedDate).format("dddd, D [de] MMMM")}
        </h2>
        <p className="text-xs text-gray-600 mb-3">Clases del día seleccionado</p>
        
        {selectedDayEvents.length > 0 ? (
          <div className="space-y-2">
            {selectedDayEvents.map((event, idx) => (
              <div
                key={idx}
                onClick={() => {
                  if (event.resource?.subjectId) {
                    navigate(`/asignaturas/${event.resource.subjectId}`);
                  }
                }}
                className="p-2 bg-gray-50 rounded-lg border-l-4 hover:shadow-md hover:bg-gray-100 transition-all cursor-pointer"
                style={{ borderLeftColor: event.resource?.color || "#3B82F6" }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800 text-sm">{event.title}</h3>
                    <p className="text-xs text-gray-600 mt-1">
                      {moment(event.start).format("HH:mm")} - {moment(event.end).format("HH:mm")}
                    </p>
                  </div>
                  <span className="material-symbols-outlined text-gray-400 text-lg">
                    chevron_right
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500">
            <svg className="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm">No hay clases programadas para este día</p>
          </div>
        )}
      </div>

      <div className="flex-1 p-4 overflow-y-auto">
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-gray-800">Calendario</h1>
          <p className="text-gray-600">Gestiona tus clases y eventos</p>
        </div>
        {loading && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-2" style={{ minHeight: "800px", maxHeight: "calc(100vh - 200px)", height: "calc(100vh - 200px)", display: "flex", flexDirection: "column" }}>
          <Calendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            style={{ flex: 1, minHeight: 0 }}
            culture="es"
            formats={formats}
            onRangeChange={handleRangeChange}
            onSelectSlot={handleSelectSlot}
            onNavigate={handleNavigate}
            selectable
            eventPropGetter={eventStyleGetter}
            messages={messages}
            views={["month"]}
            defaultView="month"
            popup={false}
            eventLimit={false}
          />
        </div>
      </div>
    </div>
  );
}
