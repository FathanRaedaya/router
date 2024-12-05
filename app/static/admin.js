/*********************
 * function weeklyRevenue:
 *
 * Calculates the estimated weekly revenue for a given time period, based on subscription data.
 *
 * Parameters:
 * * startDate (Date): The starting date for the revenue calculation period.
 * * numWeeks (number): The number of weeks to include in the calculation.
 *
 * Assumptions:
 * * The function assumes the presence of three arrays: 'weekly', 'monthly', and 'yearly' containing subscription details.
 * Returns:
 *    * x: Date object representing a week
 *    * y: The total estimated revenue for that week
 */
function weeklyRevenue(startDate, numWeeks) {
  const data = [];
  //  Get current date
  let currentDate = new Date(startDate);

  // Number of subscriptions
  let subscriptions = weekly.length + monthly.length + yearly.length;
  let sum = 0;
  let yearFound = [];

  for (let y = 0; y < numWeeks; y++) {
    let sum = 0;
    // Increment date by 7 days
    currentDate.setDate(currentDate.getDate() + 7);

    // Add 1.99 every week for every weekly subscription
    for (let i = 0; i < weekly.length; i++) {
      sum += 1.99;
    }

    // Monthly subscription calculations
    for (let i = 0; i < monthly.length; i++) {
      const monthDate = new Date(monthly[i]);
      const monthDay = monthDate.getDate();
      const currentDay = currentDate.getDate();

      // If end of month, delay subsctiption to 1st of next month
      if (monthDay == 29 || monthDay == 30 || monthDay == 31) {
        monthDay = 1;
      }

      // Calculate number of days between current day in month
      // and subscription date
      let dayDifference = currentDay - monthDay;

      // Min and max difference for monthly to be on a specific week
      let max = -23;
      let min = -30;

      // Gets the number of days in a month in a year
      function daysInMonth(month, year) {
        return new Date(year, month, 0).getDate();
      }

      // If days in month not 30, adjust min and max accordingly
      if (
        daysInMonth(currentDate.getMonth(), currentDate.getFullYear()) == 31
      ) {
        min -= 1;
        max -= 1;
      } else if (
        daysInMonth(currentDate.getMonth(), currentDate.getFullYear()) == 29
      ) {
        min += 1;
        max += 1;
      } else if (
        daysInMonth(currentDate.getMonth(), currentDate.getFullYear()) == 28
      ) {
        min += 2;
        max += 2;
      }

      // If monthly subscription within current week, add 6.49 to revenue
      if (
        (dayDifference < 7 && dayDifference >= 0) ||
        (dayDifference >= min && dayDifference < max)
      ) {
        sum += 6.49;
      }
    }

    // Calculations for yearly
    for (let i = 0; i < yearly.length; i++) {
      const monthDate = new Date(yearly[i]);
      let monthDay = monthDate.getDate();
      const currentDay = currentDate.getDate();

      // If end of month, delay subsctiption to 1st of next month
      if (monthDay == 29 || monthDay == 30 || monthDay == 31) {
        monthDay = 1;
      }

      // Calculate number of days 
      let dayDifference = currentDay - monthDay;

      // Year where payment is due (always next year)
      const paymentYear = monthDate.getFullYear() + 1;

      // Min and max difference for monthly to be on a specific week
      let max = -23;
      let min = -30;

      // Gets the number of days in a month in a year
      function daysInMonth(month, year) {
        return new Date(year, month, 0).getDate();
      }

      // If days in month not 30, adjust min and max accordingly
      if (
        daysInMonth(currentDate.getMonth(), currentDate.getFullYear()) == 31
      ) {
        min -= 1;
        max -= 1;
      } else if (
        daysInMonth(currentDate.getMonth(), currentDate.getFullYear()) == 29
      ) {
        min += 1;
        max += 1;
      } else if (
        daysInMonth(currentDate.getMonth(), currentDate.getFullYear()) == 28
      ) {
        min += 2;
        max += 2;
      }

      // If yearly subscription within current week, add 59.99 to revenue
      if (
        ((dayDifference < 7 && dayDifference >= 0) ||
          (dayDifference >= min && dayDifference < max)) &&
        currentDate.getFullYear() == paymentYear &&
        (currentDate.getMonth() == monthDate.getMonth() ||
          (currentDate.getMonth() == monthDate.getMonth() + 1 &&
            !yearFound.includes(i)))
      ) {
        sum += 59.99;
        yearFound.push(i);
      }
    }

    // push week date and sum of revenue to data array
    data.push({ x: new Date(currentDate), y: sum });
  }

  return data;
}

// Calculates future revenue for 52 weeks
const futureRevenue = weeklyRevenue(new Date(), 52);

// Subscription pie chart data
const data = {
  labels: ["weekly payments", "monthly payments", "yearly payments"],
  datasets: [
    {
      label: "Subscription Pie Chart",
      data: [weekly.length, monthly.length, yearly.length],
      backgroundColor: ["#0d6efd", "#dc3545", "#ffc107"],
      tension: 0.1,
      hoverBorderColor: "rgb(255, 99, 132)",
    },
  ],
};

// Subscription pie chart config
const config = {
  type: "doughnut",
  data: data,
  options: {
    maintainAspectRatio: false,
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: false,
      },
    },
  },
};

// Render pie chart
const pieChart = new Chart(document.getElementById("pieChart"), config);

// Line chart data
const data2 = {
  labels: futureRevenue.map((data) => data.x.toLocaleDateString("en-US")),
  datasets: [
    {
      label: "Line Chart",
      data: futureRevenue,
      fill: false,
      borderColor: "rgb(75, 192, 192)",
      tension: 0.1,
    },
  ],
};

// Line chart config
const config2 = {
  type: "line",
  data: data2,
  options: {
    plugins: {
      title: {
        color: "white",
      },
      legend: {
        labels: {
          color: "white",
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: "white",
        },
      },
      y: {
        ticks: {
          color: "white",
        },
      },
    },
  },
};

// Render line chart
const lineChart = new Chart(document.getElementById("lineChart"), config2);

// Toggle different charts
function toggleVisibility(id) {
  const allG = ['G1','G2','G3'] // id of all graphs

  var element = document.getElementById(id);
  if(element){
  
    if(!element.classList.contains('hide')){
      return;//makes sure at least one graph is visible
    }

  allG.forEach(g => {//only one graph is visible at a time
    if(g != id){
      document.getElementById(g).classList.add('hide')
    }
  })
    
    element.classList.toggle('hide');//toggle visibility
  }
 
}