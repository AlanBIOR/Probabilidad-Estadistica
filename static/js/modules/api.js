export async function executeProcess(payload, isFile = false) {
  let response;

  if (isFile) {
    response = await fetch("/api/process", {
      method: "POST",
      body: payload, // FormData
    });
  } else {
    response = await fetch("/api/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error || "Ocurrió un error en el procesamiento.");
  }
  return data;
}