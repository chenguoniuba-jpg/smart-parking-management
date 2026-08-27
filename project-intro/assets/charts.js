(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var chartEl = document.getElementById('chart-skills');
  if (!chartEl) return;

  var chart = echarts.init(chartEl, null, { renderer: 'svg' });

  chart.setOption({
    animation: false,
    tooltip: {
      trigger: 'item',
      appendToBody: true
    },
    radar: {
      indicator: [
        { name: 'Full-Stack\nDevelopment', max: 100 },
        { name: 'AI / ML\nAlgorithms', max: 100 },
        { name: 'Database\nDesign', max: 100 },
        { name: 'API\nArchitecture', max: 100 },
        { name: 'UI / UX\nDesign', max: 100 },
        { name: 'Behavioral\nScience', max: 100 }
      ],
      shape: 'polygon',
      radius: '65%',
      center: ['50%', '52%'],
      splitNumber: 4,
      axisName: {
        color: ink,
        fontSize: 12,
        fontWeight: 600,
        lineHeight: 16
      },
      splitLine: {
        lineStyle: {
          color: rule,
          width: 1
        }
      },
      splitArea: {
        areaStyle: {
          color: [bg2, 'transparent', bg2, 'transparent']
        }
      },
      axisLine: {
        lineStyle: {
          color: rule
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [92, 78, 88, 90, 75, 82],
        name: 'Skill Coverage',
        areaStyle: {
          color: accent + '20'
        },
        lineStyle: {
          color: accent,
          width: 2
        },
        itemStyle: {
          color: accent,
          borderColor: bg2,
          borderWidth: 2
        },
        symbolSize: 7
      }]
    }]
  });

  window.addEventListener('resize', function() {
    chart.resize();
  });
})();
