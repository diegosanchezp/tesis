const form_paths = {
  egresados: ["carrera", "experiencia", "profile"],
  estudiantes: ["carrera", "experiencia", "",],
  empresas: [""]
}

const MachineStates = {
  completed: "completed",
  notCompleted: "not_completed",
  partCompleted: "partial_completion",
};

const stateMachine = {
  [MachineStates.notCompleted]: {
    write: MachineStates.partCompleted,
  },
  [MachineStates.partCompleted]: {
    submitForm: MachineStates.completed
  },
  [MachineStates.completed]: {
    modifyForm: MachineStates.partCompleted
  }
};

type formDataEstudiante = {
  carrera: string,
  especialiciazion: string,
  temas_interes: string[],
  nombre: string
  apellido: string
  email: string
}

type experienciaMentor = {
  nombre: string,
  actual: boolean,
  year_inicio: Date,
  year_fin: Date,
  descripcion: string
}

type formDataMentor = {
  carrera: string,
  experiencia: experienciaMentor[],
}

type localStorage = {
  currentStep: string
  lastStep: string | null,
  formStatus: "completed" | "not_completed" | "partial_completion",
}


function getStorageData() {
  return {
  }
}

