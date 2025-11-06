// Este script espera que la variable 'clienteId' sea inyectada
// como un de numero, ej: clienteId = 1;

db.ticket.aggregate([
    {
        $match: {
            cliente_id: clienteId,
            // cliente_id: 1,
            $expr: {
                $eq: [ { $month: "$fecha" }, 9 ] // Filtra donde el mes de 'fecha' sea 9 (Septiembre)
            }
        }
    }
]).forEach(printjson);