import React from 'react'
import Link from 'next/link'
import Layout from '../components/Layout'
import fetchPageData from '../util/fetchPageData'

export default class extends React.Component {

  static async getInitialProps({ req }) {
    return await fetchPageData(req, { courses: 'list_courses' })
  }

  render() {
    const { user, courses } = this.props
    return (
      <Layout user={user}>
        <h1>Pyladies courseware</h1>

        <h2>Aktuálně běžící kurzy</h2>

        {courses.active.map(course => (
          <p key={course.id}>
            <Link href={{ pathname: '/course', query: { course: course.id }}}><a>
              <strong dangerouslySetInnerHTML={{__html: course.title_html}} />
              {' – '}
              <span dangerouslySetInnerHTML={{__html: course.subtitle_html}} />
            </a></Link>
          </p>
        ))}

        <h2>Proběhlé kurzy</h2>

        <p>TBD&hellip;</p>

      </Layout>
    )
  }
}
