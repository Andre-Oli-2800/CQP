
const ctx = document.getElementById('myChart');

var chartGraph = new Chart(ctx, {
  type: 'bar',
  data: {
    {% for nomeMaisVendido in nomeMaisVendidos %}
    labels: [{{nomeMaisVendido}}],
    {% endfor %}
    datasets: [{
      label: '# of Votes',
      {% for maisVendidoLista in maisVendidoListas %}
      data: [maisVendidoLista],
      {% endfor %}
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});