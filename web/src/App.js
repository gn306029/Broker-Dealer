import './App.css';
import { StockChart } from './components/stockChart';
import { useState, useEffect } from 'react';
import { Box } from '@mui/system';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';

const broker_name_table = {
    "9216": "凱基信義",
    "0039004100390052": "永豐金信義",
    "8564": "新光台南",
    "003700370039005a": "國票安和",
}

const random_rgba = () => {
  var o = Math.round, r = Math.random, s = 255;
  return `rgba(${o(r()*s)}, ${o(r()*s)}, ${o(r()*s)}, 0.5)`;
}

const get_curr_date = () => {
  return new Date().toISOString().slice(0, 10)
}

const format_data_type_1 = (data) => {
  // 將資料整理為以下格式
  // {
  //   ["股票代號 1", "股票代號 2", ...],
  //     datasets: [
  //       {
  //         label: '券商 1',
  //         data: [10,20,30,40,1000],
  //         backgroundColor: 'rgba(255, 99, 132, 0.5)',
  //       },
  //       {
  //         label: '券商 2',
  //         data: [10,20,30,40,50],
  //         backgroundColor: 'rgba(53, 162, 235, 0.5)',
  //       },
  //     ]
  // }
  let result = {
    labels: ["買入", "賣出", "差額"],
    datasets: []
  }

  data.forEach(row => {
    // result.labels.push(row[0])
    row[1].forEach(trade_row => {
      let [seller_id, stock_id, trade_info] = trade_row

      result.datasets.push({
        label: broker_name_table[seller_id],
        data: [
          trade_info.buying_amount, 
          trade_info.selling_amount,
          trade_info.diff_amount
        ],
        backgroundColor: random_rgba()
      })
    })
  })

  return result
}

function App() {

  const fetchData = () => {
    setStockInfo([])

    let url = `http://127.0.0.1:8000/get?start_date=${startDate}&end_date=${endDate}`

    fetch(url).then(res => {
      res.json().then(data => {
        setStockInfo(data)
      })
    })
  }

  const [stockInfo, setStockInfo] = useState([])
  const [chartList, setChartListInfo] = useState("Default")
  const [startDate, setStartDate] = useState(get_curr_date())
  const [endDate, setEndDate] = useState(get_curr_date())

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    let chartList = []

    stockInfo.forEach(row => {
      let d = format_data_type_1([row])
      let title = row[0].replaceAll("'", "")

      chartList.push(
        <StockChart key={title} data={d} title={title} labels={d.labels}></StockChart>
      )
    })

    setChartListInfo(chartList)
  }, [stockInfo])

  return (
    <div className="App">
      <Box sx={{ m: "auto", pb: "1rem"}}>
        <Box sx={{display: 'inline-flex', m: '.5rem'}}>
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}></input>
        </Box>
        <Box sx={{display: 'inline-flex', m: '.5rem'}}>
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}></input>
        </Box>
        <Box sx={{display: 'inline-flex', m: '.5rem'}}><Button variant="outlined" onClick={() => fetchData()}>查詢</Button></Box>
      </Box>
      <Box sx={{ m: "auto", pb: "1rem"}}>
        {chartList}
      </Box>
    </div>
  );
}

export default App;
