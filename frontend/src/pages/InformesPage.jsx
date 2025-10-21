import React, { useState, useEffect } from 'react';
import api from '../lib/axios';
import Select from 'react-select';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
// TEMPORALMENTE COMENTADO PARA VERCEL BUILD
// import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// Dummy widgets for structure
const AlumnoHeader = ({ alumno }) => (
  <div className="flex items-center gap-4 mb-6">
    <img src={alumno.foto} alt="Foto" className="w-16 h-16 rounded-full object-cover" />
    <div>
      <h2 className="text-xl font-bold">{alumno.nombre}</h2>
      <div className="text-gray-600 text-sm">Grupo: {alumno.grupo} | Asignaturas: {alumno.asignaturas?.join(', ')}</div>
    </div>
  </div>
);

const ResumenIA = ({ resumen }) => (
  <div className="bg-blue-50 p-4 rounded-lg mb-4">
    <h3 className="font-semibold text-blue-800 mb-2">Resumen IA</h3>
    <p className="mb-2">{resumen.resumen_general}</p>
    <div className="text-blue-700 font-medium">Recomendaciones: {resumen.recomendaciones}</div>
  </div>
);

const FortalezasAreas = ({ fortalezas, areas }) => (
  <div className="grid grid-cols-2 gap-4 mb-4">
    <div>
      <h4 className="font-semibold text-green-700 mb-2">Fortalezas</h4>
      <ul className="list-disc pl-5 text-green-800">
        {fortalezas.map((f, i) => <li key={i}>{f}</li>)}
      </ul>
    </div>
    <div>
      <h4 className="font-semibold text-red-700 mb-2">Áreas de mejora</h4>
      <ul className="list-disc pl-5 text-red-800">
        {areas.map((a, i) => <li key={i}>{a}</li>)}
      </ul>
    </div>
  </div>
);

const NotasChart = ({ data }) => (
  <div className="bg-white p-4 rounded-lg mb-4 shadow">
    <h4 className="font-semibold mb-2">Evolución de notas</h4>
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <XAxis dataKey="fecha" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="nota" stroke="#2563eb" />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

const AsistenciaChart = ({ presente, ausente }) => (
  <div className="bg-white p-4 rounded-lg mb-4 shadow">
    <h4 className="font-semibold mb-2">Asistencia</h4>
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={[{ name: 'Presente', value: presente }, { name: 'Ausente', value: ausente }]} dataKey="value" cx="50%" cy="50%" outerRadius={60} label>
          <Cell key="Presente" fill="#22c55e" />
          <Cell key="Ausente" fill="#ef4444" />
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

const EvidenciasGrid = ({ evidencias }) => (
  <div className="bg-white p-4 rounded-lg mb-4 shadow">
    <h4 className="font-semibold mb-2">Evidencias</h4>
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
      {evidencias.map((ev, i) => (
        <a key={i} href={ev.url} target="_blank" rel="noopener noreferrer" className="block">
          {ev.tipo === 'foto' ? (
            <img src={ev.url} alt="Evidencia" className="w-full h-24 object-cover rounded" />
          ) : (
            <div className="bg-gray-100 p-2 rounded text-xs text-center">Documento</div>
          )}
        </a>
      ))}
    </div>
  </div>
);

const AudiosList = ({ audios }) => (
  <div className="bg-white p-4 rounded-lg mb-4 shadow">
    <h4 className="font-semibold mb-2">Audios</h4>
    <ul>
      {audios.map((a, i) => (
        <li key={i} className="mb-2 flex items-center gap-2">
          <audio controls src={a.url} className="h-8" />
          <span className="text-gray-700 text-sm">{a.transcripcion}</span>
        </li>
      ))}
    </ul>
  </div>
);

const ExportButtons = () => (
  <div className="flex gap-4 mb-6">
    <button className="bg-red-600 text-white px-4 py-2 rounded font-semibold">📤 Exportar PDF</button>
    <button className="bg-blue-600 text-white px-4 py-2 rounded font-semibold">📊 Exportar Excel</button>
    <button className="bg-green-600 text-white px-4 py-2 rounded font-semibold">💾 Guardar informe</button>
  </div>
);

export default function InformesPage() {
  // Estados de filtros y datos
  const [alumnos, setAlumnos] = useState([]);
  const [asignaturas, setAsignaturas] = useState([]);
  const [grupos, setGrupos] = useState([]);
  const [selectedAlumno, setSelectedAlumno] = useState(null);
  const [selectedAsignaturas, setSelectedAsignaturas] = useState([]);
  const [selectedGrupo, setSelectedGrupo] = useState(null);
  const [dateRange, setDateRange] = useState([null, null]);
  const [analizarIA, setAnalizarIA] = useState(true);
  const [loading, setLoading] = useState(false);
  const [informe, setInforme] = useState(null);
  const [alumnoData, setAlumnoData] = useState(null);

  // Cargar filtros dinámicos
  useEffect(() => {
    api.get('/students').then(res => {
      const arr = res.data.results || res.data;
      setAlumnos(arr.map(a => ({ label: a.name, value: a.id, ...a })));
    });
    api.get('/subjects').then(res => {
      const arr = res.data.results || res.data;
      setAsignaturas(arr.map(a => ({ label: a.name, value: a.id })));
    });
    api.get('/groups').then(res => {
      const arr = res.data.results || res.data;
      setGrupos(arr.map(g => ({ label: g.name, value: g.id })));
    });
  }, []);

  // Generar informe al pulsar el botón
  const generarInforme = async () => {
    if (!selectedAlumno) return;
    setLoading(true);
    try {
      // Obtener datos completos del alumno
      const res = await api.get(`/alumnos/${selectedAlumno.value}/datos_completos`);
      setAlumnoData(res.data);
      // Si IA activada, pedir resumen IA
      if (analizarIA) {
        const iaRes = await api.post('/informes/ia/generar', res.data);
        setInforme(iaRes.data);
      } else {
        setInforme(null);
      }
    } catch (e) {
      setAlumnoData(null);
      setInforme(null);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
  <h1 className="text-2xl font-bold mb-6 text-black">Informes Inteligentes</h1>
      {/* Filtros superiores */}
      <div className="flex flex-wrap gap-4 mb-8 items-end">
        <div className="min-w-[180px]">
          <label className="block text-sm font-medium mb-1">Alumno</label>
          <Select options={alumnos} value={selectedAlumno} onChange={setSelectedAlumno} placeholder="Selecciona alumno..." classNamePrefix="custom-select" styles={{control: (base) => ({...base, backgroundColor: '#fff', color: '#000', borderColor: '#888', fontWeight: 600}), placeholder: (base) => ({...base, color: '#6b7280'}), option: (base, state) => ({...base, backgroundColor: state.isSelected ? '#2563eb' : state.isFocused ? '#e0e7ff' : '#fff', color: state.isSelected ? '#fff' : '#000', fontWeight: state.isSelected ? 700 : 500})}} />
        </div>
        <div className="min-w-[180px]">
          <label className="block text-sm font-medium mb-1">Asignatura</label>
          <Select isMulti options={asignaturas} value={selectedAsignaturas} onChange={setSelectedAsignaturas} placeholder="Selecciona asignaturas..." classNamePrefix="custom-select" styles={{control: (base) => ({...base, backgroundColor: '#fff', color: '#000', borderColor: '#888', fontWeight: 600}), placeholder: (base) => ({...base, color: '#6b7280'}), option: (base, state) => ({...base, backgroundColor: state.isSelected ? '#2563eb' : state.isFocused ? '#e0e7ff' : '#fff', color: state.isSelected ? '#fff' : '#000', fontWeight: state.isSelected ? 700 : 500})}} />
        </div>
        <div className="min-w-[180px]">
          <label className="block text-sm font-medium mb-1">Grupo</label>
          <Select options={grupos} value={selectedGrupo} onChange={setSelectedGrupo} placeholder="Selecciona grupo..." classNamePrefix="custom-select" styles={{control: (base) => ({...base, backgroundColor: '#fff', color: '#000', borderColor: '#888', fontWeight: 600}), placeholder: (base) => ({...base, color: '#6b7280'}), option: (base, state) => ({...base, backgroundColor: state.isSelected ? '#2563eb' : state.isFocused ? '#e0e7ff' : '#fff', color: state.isSelected ? '#fff' : '#000', fontWeight: state.isSelected ? 700 : 500})}} />
        </div>
        <div className="min-w-[220px]">
          <label className="block text-sm font-medium mb-1">Rango de fechas</label>
          <DatePicker selectsRange startDate={dateRange[0]} endDate={dateRange[1]} onChange={(update) => setDateRange(update)} isClearable placeholderText="Selecciona rango..." className="w-full p-2 border border-gray-400 rounded text-black bg-white placeholder-gray-500 font-semibold" />
        </div>
        <div className="flex items-center gap-2">
          <input type="checkbox" checked={analizarIA} onChange={e => setAnalizarIA(e.target.checked)} className="h-5 w-5 accent-blue-600 border-2 border-gray-600 bg-white focus:ring-2 focus:ring-blue-500" />
         <span className="text-sm"></span>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded font-semibold" onClick={generarInforme} disabled={loading}>Generar informe</button>
      </div>
      {/* Widgets de informe con datos reales */}
      {loading && <div className="text-center py-8">Cargando informe...</div>}
      {alumnoData && <AlumnoHeader alumno={{
        foto: alumnoData.foto || 'https://randomuser.me/api/portraits/lego/1.jpg',
        nombre: alumnoData.nombre,
        grupo: alumnoData.grupo || '',
        asignaturas: alumnoData.asignaturas || []
      }} />}
      {informe && <ResumenIA resumen={informe} />}
      {informe && <FortalezasAreas fortalezas={informe.fortalezas || []} areas={informe.areas_de_mejora || []} />}
      {alumnoData && <NotasChart data={alumnoData.evaluaciones || []} />}
      {alumnoData && <AsistenciaChart presente={alumnoData.asistencias?.filter(a => a.presente).length || 0} ausente={alumnoData.asistencias?.filter(a => !a.presente).length || 0} />}
      {alumnoData && <EvidenciasGrid evidencias={alumnoData.evidencias || []} />}
      {alumnoData && <AudiosList audios={alumnoData.audios || []} />}
      <ExportButtons />
      <footer className="mt-8 text-xs text-gray-400 text-center">Versión 1.0 • {new Date().toLocaleDateString()}</footer>
    </div>
  );
}
