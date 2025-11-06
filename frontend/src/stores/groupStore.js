import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import api from '../lib/axios';

/**
 * Store de Zustand para gestión de grupos
 * Centraliza estado y reduce refetchs innecesarios
 */
const useGroupStore = create(
  devtools(
    (set, get) => ({
      // Estado
      groups: [],
      currentGroup: null,
      availableStudents: [],
      loading: false,
      error: null,

      // Acciones
      setLoading: (loading) => set({ loading }),
      
      setError: (error) => set({ error }),

      // Fetch todos los grupos
      fetchGroups: async () => {
        set({ loading: true, error: null });
        try {
          const response = await api.get('/grupos/');
          const groupsData = Array.isArray(response.data) ? response.data : [];
          set({ groups: groupsData, loading: false });
          return groupsData;
        } catch (error) {
          console.error('[groupStore] fetchGroups error:', error);
          set({ error: error.message, loading: false, groups: [] }); // Asegurar que groups sea array
          throw error;
        }
      },

      // Fetch grupo con detalles completos (estudiantes, subjects, etc)
      fetchGroupDetails: async (groupId) => {
        set({ loading: true, error: null });
        try {
          // Usar Promise.all para cargar todo en paralelo
          // Endpoint unificado: ?exclude_from_group en lugar de /available_for_group/
          const [groupResponse, studentsResponse, availableResponse] = await Promise.all([
            api.get(`/grupos/${groupId}`),
            api.get(`/grupos/${groupId}/alumnos/`),
            api.get(`/estudiantes/?exclude_from_group=${groupId}`)
          ]);

          const groupData = {
            ...groupResponse.data,
            students: studentsResponse.data.students || [],
            counts: studentsResponse.data.counts || {},
            total_students: (studentsResponse.data.students || []).length
          };

          set({ 
            currentGroup: groupData,
            availableStudents: availableResponse.data || [],
            loading: false 
          });
          
          return groupData;
        } catch (error) {
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      // Crear grupo
      createGroup: async (groupData) => {
        set({ loading: true, error: null });
        console.log('[groupStore] createGroup - groupData:', groupData);
        try {
          const response = await api.post('/grupos/', groupData);
          const newGroup = response.data;
          console.log('[groupStore] createGroup - response:', newGroup);
          
          // Actualizar lista de grupos (con validación defensiva)
          set((state) => {
            const updatedGroups = Array.isArray(state.groups) ? [...state.groups, newGroup] : [newGroup];
            console.log('[groupStore] createGroup - updating state. Old groups:', state.groups, 'New groups:', updatedGroups);
            return {
              groups: updatedGroups,
              loading: false
            };
          });
          
          console.log('[groupStore] createGroup - state after update:', get().groups);
          return newGroup;
        } catch (error) {
          console.error('[groupStore] createGroup error:', error);
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      // Actualizar grupo
      updateGroup: async (groupId, groupData) => {
        set({ loading: true, error: null });
        try {
          const response = await api.put(`/grupos/${groupId}/`, groupData);
          const updatedGroup = response.data;
          
          // Actualizar en la lista (con validación defensiva)
          set((state) => ({
            groups: Array.isArray(state.groups) 
              ? state.groups.map((g) => g.id === groupId ? updatedGroup : g)
              : [updatedGroup],
            currentGroup: state.currentGroup?.id === groupId ? updatedGroup : state.currentGroup,
            loading: false
          }));
          
          return updatedGroup;
        } catch (error) {
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      // Eliminar grupo
      deleteGroup: async (groupId) => {
        set({ loading: true, error: null });
        try {
          await api.delete(`/grupos/${groupId}/`);
          
          set((state) => ({
            groups: Array.isArray(state.groups) ? state.groups.filter((g) => g.id !== groupId) : [],
            currentGroup: state.currentGroup?.id === groupId ? null : state.currentGroup,
            loading: false
          }));
        } catch (error) {
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      // Añadir estudiante a grupo
      addStudentToGroup: async (groupId, studentId) => {
        try {
          await api.post(`/grupos/${groupId}/add_student/`, { student_id: studentId });
          
          // Refrescar datos del grupo
          await get().fetchGroupDetails(groupId);
        } catch (error) {
          set({ error: error.message });
          throw error;
        }
      },

      // Crear estudiante en grupo
      createStudentInGroup: async (groupId, studentData) => {
        try {
          const response = await api.post('/estudiantes/', {
            ...studentData,
            grupo_principal: groupId
          });
          
          // Refrescar datos del grupo
          await get().fetchGroupDetails(groupId);
          
          return response.data;
        } catch (error) {
          set({ error: error.message });
          throw error;
        }
      },

      // Eliminar estudiante de grupo
      removeStudentFromGroup: async (groupId, studentId) => {
        try {
          await api.post(`/grupos/${groupId}/remove_student/`, { student_id: studentId });
          
          // Refrescar datos del grupo
          await get().fetchGroupDetails(groupId);
        } catch (error) {
          set({ error: error.message });
          throw error;
        }
      },

      // Limpiar grupo actual
      clearCurrentGroup: () => set({ currentGroup: null, availableStudents: [] }),

      // Reset store
      reset: () => set({
        groups: [],
        currentGroup: null,
        availableStudents: [],
        loading: false,
        error: null
      })
    }),
    { name: 'GroupStore' }
  )
);

// Selectores optimizados (evitan re-renders innecesarios)
export const selectGroups = (state) => state.groups;
export const selectCurrentGroup = (state) => state.currentGroup;
export const selectAvailableStudents = (state) => state.availableStudents;
export const selectLoading = (state) => state.loading;
export const selectError = (state) => state.error;

// Selectores derivados con memoización
export const selectGroupById = (groupId) => (state) => 
  state.groups.find((g) => g.id === groupId);

export const selectGroupStudents = (state) => 
  state.currentGroup?.students || [];

export const selectGroupCounts = (state) => 
  state.currentGroup?.counts || {};

export default useGroupStore;
